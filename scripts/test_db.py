"""
Test database connection and verify all figma tables exist.
Run: python scripts/test_db.py
"""
import asyncio
from sqlalchemy import text
from src.database.base import AsyncSessionLocal


async def main():
    print("Testing database connection...")

    async with AsyncSessionLocal() as session:
        try:
            # Basic connection test
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connected successfully")

            # Verify all our tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'figma_%'
                ORDER BY table_name
            """)
            result = await session.execute(tables_query)
            tables = [row[0] for row in result.fetchall()]

            expected = [
                "figma_ai_reviews",
                "figma_client_responses",
                "figma_designer_notes",
                "figma_review_tokens",
                "figma_screens",
                "figma_tasks",
            ]

            print(f"\nFigma tables found in database:")
            for table in expected:
                status = "✅" if table in tables else "❌ MISSING"
                print(f"  {status} {table}")

            if all(t in tables for t in expected):
                print("\n✅ All tables present. Database ready.")
            else:
                print("\n❌ Some tables missing. Check migration ran correctly.")

        except Exception as e:
            print(f"❌ Database error: {e}")


if __name__ == "__main__":
    asyncio.run(main())