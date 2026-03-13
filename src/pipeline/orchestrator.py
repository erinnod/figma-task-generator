import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.figma.client import FigmaClient, FigmaClientError
from src.figma.parser import FigmaParser
from src.llm.context_builder import ContextBuilder
from src.llm.client import LLMClient
from src.llm.review_generator import ReviewGenerator
from src.storage.azure_blob import AzureBlobStorage
from src.database.models import Screen, AIReview
from src.config import settings


class PipelineError(Exception):
    pass

class PipelineOrchestrator:
    """
    Coordinates the full Figma → AI Review pipeline.

    Stage 1: Fetch raw Figma JSON
    Stage 2: Parse and extract screens
    Stage 3: Export and store screenshots
    Stage 4: Generate AI review per screen
    Stage 5: Store everything in database
    """

    def __init__(self):
        self.figma_client = FigmaClient()
        self.parser = FigmaParser()
        self.context_builder = ContextBuilder()
        self.llm_client = LLMClient()
        self.review_generator = ReviewGenerator(self.llm_client)
        self.storage = AzureBlobStorage()

    async def run(
        self,
        project_id: str,
        figma_url: str,
        db: AsyncSession
    ) -> dict:
        """
        Main entry point. Runs the full pipeline for a project.

        Args:
            project_id: The OnTarget project ID
            figma_url: The Figma file URL pasted by the designer
            db: Database session

        Returns:
            Summary dict with counts and status
        """
        print(f"\n{'='*50}")
        print(f"Starting pipeline for project: {project_id}")
        print(f"{'='*50}\n")

        # ── Stage 1: Fetch Figma file ──────────────────────
        print("Stage 1: Fetching Figma file...")
        try:
            file_key = FigmaClient.extract_file_key(figma_url)
            raw_data = await self.figma_client.get_file(file_key)
            print(f"Fetched: {raw_data.get('name')}")
        except FigmaClientError as e:
            raise PipelineError(f"Figma fetch failed: {e}")
        
        # ── Stage 2: Parse design ──────────────────────────
        print("\nStage 2: Parsing design...")
        design_context = self.parser.parse(raw_data)
        print(f"Parsed {design_context.total_screens} screens")
        print(f"Features: {design_context.inferred_features}")

        if design_context.total_screens == 0:
            raise PipelineError(
                "No valid screens found in this Figma file. "
                "Check the file has real design pages."
            )
        
        # ── Stage 3: Export and store screenshots ──────────
        print("\nStage 3: Exporting screenshots...")
        node_ids = [
            screen.id
            for screen in design_context.screens
        ]

        try:
            image_urls = await self.figma_client.export_screen_images(
                file_key, node_ids
            )
            print(f"Exported {len(image_urls)} screenshots")
        except FigmaClientError as e:
            # Non-fatal — we can continue without screenshots
            print(f"Screenshot export failed: {e}")
            image_urls = {}
        
        # ── Stage 4: Save screens to database ─────────────
        print("\nStage 4: Saving screens to database...")
        saved_screens = []

        for index, design_screen in enumerate(design_context.screens):
            # Store screenshot in Azure if we got the image
            blob_path = None
            temp_url = image_urls.get(design_screen.id)

            if temp_url:
                try:
                    safe_node_id = design_screen.id.replace(":", "-")
                    blob_path = await self.storage.store_figma_screenshot(
                        figma_image_url=temp_url,
                        project_id=project_id,
                        screen_id=safe_node_id
                    )
                except Exception as e:
                    print(f"Screenshot storage failed for "
                          f"{design_screen.name}: {e}")
            
            # Create screen record in database
            screen = Screen(
                id=str(uuid.uuid4()),
                project_id=project_id,
                figma_node_id=design_screen.id,
                name=design_screen.name,
                page_name=design_screen.page,
                blob_path=blob_path,
                order_index=index,
                status="PENDING"
            )
            db.add(screen)
            saved_screens.append(screen)
        
        await db.flush()  # Write screens before creating reviews
        print(f"Saved {len(saved_screens)} screens")

        # ── Stage 5: Generate AI review per screen ─────────
        print("\nStage 5: Generating AI reviews...")
        reviews_generated = 0

        for screen in saved_screens:
            # find matching design screen for context
            design_screen = next(
                (s for s in design_context.screens
                if s.id == screen.figma_node_id),
                None
            )
            if not design_screen:
                continue

            try:
                # Build context for this specific screen
                screen_context = self.context_builder.build_screen_context(
                    design_screen, design_context
                )

                # Generate assumptions and questions
                review_data = await self.review_generator.generate(
                    screen_name=screen.name,
                    page_name=screen.page_name or "",
                    screen_context=screen_context
                )

                # Save review to database
                ai_review = AIReview(
                    id=str(uuid.uuid4()),
                    screen_id=screen.id,
                    assumptions=review_data.get("assumptions", []),
                    questions=review_data.get("questions", []),
                    confidence_scores=review_data.get(
                        "confidence_scores", {}
                    )
                )
                db.add(ai_review)

                # Update screen status
                screen.status = "QUESTIONS_GENERATED"
                reviews_generated += 1

                print(f"{screen.name} — "
                      f"{len(review_data.get('questions', []))} questions")
            
            except Exception as e:
                print(f"Review generation failed for "
                      f"{screen.name}: {e}")
                screen.status = "PENDING"

        await db.flush()
        print(f"\n Generated {reviews_generated} AI reviews")

        # ── Done ───────────────────────────────────────────
        summary = {
            "project_id": project_id,
            "file_name": design_context.file_name,
            "screens_found": design_context.total_screens,
            "screenshots_stored": len([
                s for s in saved_screens if s.blob_path
            ]),
            "reviews_generated": reviews_generated,
            "status": "READY_FOR_CLIENT_REVIEW"
        }

        print(f"\n{'='*50}")
        print(f"Pipeline complete: {summary}")
        print(f"{'='*50}\n")

        return summary
