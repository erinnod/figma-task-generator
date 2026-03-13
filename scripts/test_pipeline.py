"""
End-to-end pipeline test.
Run: python scripts/test_pipeline.py
"""
import asyncio
from src.pipeline.orchestrator import PipelineOrchestrator, PipelineError
from src.database.base import AsyncSessionLocal


async def main():
    figma_url = input("Enter Figma URL: ").strip()
    project_id = input("Enter a test project ID: ").strip()

    orchestrator = PipelineOrchestrator()

    async with AsyncSessionLocal() as db:
        try:
            summary = await orchestrator.run(
                project_id=project_id,
                figma_url=figma_url,
                db=db
            )
            await db.commit()
            print(f"\n✅ Pipeline complete:")
            for key, value in summary.items():
                print(f"  {key}: {value}")

        except PipelineError as e:
            print(f"\n❌ Pipeline failed: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())