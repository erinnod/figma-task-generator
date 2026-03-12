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
        Returns the raw JSON response as a dictionary.
        """
        if not self.token:
            raise FigmaClientError("Figma API token is not set")

        url = f"{self.BASE_URL}/files/{file_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0,
            )
        
        if response.status_code == 403:
            raise FigmaClientError("Access denied. Check your API token.")

        if response.status_code == 404:
            raise FigmaClientError(f"File not found: {file_key}")

        if response.status_code != 200:
            raise FigmaClientError(f"Failed to fetch file: {response.status_code} {response.text}")

        return response.json()

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
            # file key always follows 'file' or 'design' segment
            for i, part in enumerate(parts):
                if part in ('file', 'design'):
                    return parts[i+1]
            raise FigmaClientError(f"Could not extract file key from URL: {figma_url}")
        except IndexError:
            raise FigmaClientError(f"Invalid Figma URL: {figma_url}")