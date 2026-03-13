import httpx
from src.config import settings


class FigmaClientError(Exception):
    """Exception raised when Figma API returns an error."""
    pass


class FigmaClient:
    """
    Client for interacting with the Figma REST API.

    Responsible for a single thing: fetching raw design
    data from Figma. No parsing, no transformation.
    """

    BASE_URL = "https://api.figma.com/v1"

    def __init__(self):
        self.token = settings.figma_api_token
        self.headers = {
            "X-Figma-Token": self.token
        }

    async def get_file(self, file_key: str) -> dict:
        """
        Fetch a Figma file by its key.
        """
        if not self.token:
            raise FigmaClientError(
                "FIGMA_API_TOKEN is not set. "
                "Add it to your .env file."
            )

        url = f"{self.BASE_URL}/files/{file_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0,
            )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            details = [
                "Figma rate limit (429) response:",
                f"Status: {response.status_code}",
                "Headers:",
            ]
            for name, value in response.headers.items():
                details.append(f"  {name}: {value}")
            details.extend(["Body:", response.text])
            raise FigmaClientError("\n".join(details))

        if response.status_code == 403:
            raise FigmaClientError(
                "Invalid Figma token or insufficient permissions."
            )

        if response.status_code == 404:
            raise FigmaClientError(
                f"Figma file '{file_key}' not found."
            )

        raise FigmaClientError(
            f"Figma API error: {response.status_code} - {response.text}"
        )

    async def export_screen_images(
        self, file_key: str, node_ids: list[str]
    ) -> dict[str, str]:
        """
        Export nodes as PNG images via Figma Images API.
        Returns a dict mapping node_id -> image URL.
        """
        if not self.token:
            raise FigmaClientError(
                "FIGMA_API_TOKEN is not set. Add it to your .env file."
            )
        if not node_ids:
            return {}
        ids_param = ",".join(node_ids)
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {"ids": ids_param, "format": "png"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params,
                timeout=60.0,
            )
        if response.status_code == 200:
            data = response.json()
            if data.get("err"):
                raise FigmaClientError(
                    f"Figma images API error: {data.get('err')}"
                )
            return data.get("images") or {}
        if response.status_code == 429:
            details = [
                "Figma rate limit (429) on images export:",
                f"Status: {response.status_code}",
                "Headers:",
            ]
            for name, value in response.headers.items():
                details.append(f"  {name}: {value}")
            details.extend(["Body:", response.text])
            raise FigmaClientError("\n".join(details))
        if response.status_code == 403:
            raise FigmaClientError(
                "Invalid Figma token or insufficient permissions."
            )
        if response.status_code == 404:
            raise FigmaClientError(
                f"Figma file '{file_key}' not found."
            )
        raise FigmaClientError(
            f"Figma API error: {response.status_code} - {response.text}"
        )

    @staticmethod
    def extract_file_key(figma_url: str) -> str:
        """
        Extract the file key from a full Figma URL.

        Handles both URL formats:
        - https://www.figma.com/file/ABC123/Name
        - https://www.figma.com/design/ABC123/Name
        """
        try:
            parts = figma_url.strip("/").split("/")
            for i, part in enumerate(parts):
                if part in ('file', 'design'):
                    return parts[i + 1]
            raise FigmaClientError(f"Could not extract file key from URL: {figma_url}")
        except IndexError:
            raise FigmaClientError(f"Invalid Figma URL: {figma_url}")
