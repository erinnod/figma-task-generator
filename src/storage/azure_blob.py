from __future__ import annotations


class AzureBlobStorage:
    """
    Minimal stub implementation so the pipeline can run without
    a real Azure Blob backend. It just returns the original
    Figma image URL as the "blob_path".
    """

    async def store_figma_screenshot(
        self,
        figma_image_url: str,
        project_id: str,
        screen_id: str,
    ) -> str:
        # In a real implementation, this would download the image
        # and upload it to Azure Blob Storage, then return the blob URL.
        # For now we just propagate the Figma URL so the rest of the
        # pipeline and database logic can be exercised.
        return figma_image_url
