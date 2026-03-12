"""
Quick script to verify Figma API connection is working.
Run with: python scripts/test_figma.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path so that 'src' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.figma.client import FigmaClient, FigmaClientError
from src.figma.parser import FigmaParser

async def main():
    client = FigmaClient()
    parser = FigmaParser()

    figma_url = input("Enter your Figma URL: ").strip()

    file_key = FigmaClient.extract_file_key(figma_url)
    print(f"\nFetching file: {file_key}")

    try:
        raw_data = await client.get_file(file_key)
        print(f"Fetched: {raw_data.get('name')}")

        print("\nParsing design...")
        context = parser.parse(raw_data)

        print(f"\nDesign Context Summary:")
        print(f"  File: {context.file_name}")
        print(f"  Valid pages: {context.pages}")
        print(f"  Total screens: {context.total_screens}")
        print(f"  Inferred features: {context.inferred_features}")
        print(f"  Component summary: {context.component_summary}")

    except FigmaClientError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())