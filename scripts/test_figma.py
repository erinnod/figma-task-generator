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

async def main():
    client = FigmaClient()

    figma_url = input("Enter your Figma URL: ").strip()

    print(f"Extracting file key from URL: {figma_url}")
    file_key = FigmaClient.extract_file_key(figma_url)
    print(f"File key: {file_key}")

    print(f"Fetching file: {file_key}")

    try:
        data = await client.get_file(file_key)

        print(f"\n Success!")
        print(f"File name: {data.get('name', 'Unknown')}")
        print(f"File last modified: {data.get('lastModified', 'Unknown')}")

        # Show top level structure
        document = data.get('document', {})
        pages = document.get('children', [])
        print(f"Number of pages: {len(pages)}")

        for page in pages:
            frames = page.get('children', [])
            print(f"Page '{page.get('name', 'Unknown')}': {len(frames)} top-level frames")

    except FigmaClientError as e:
        print(f"\n Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())