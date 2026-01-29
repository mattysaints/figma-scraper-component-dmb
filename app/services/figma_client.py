import httpx
from typing import Any

from app.core.config import settings


FIGMA_API_BASE_URL = "https://api.figma.com/v1"


class FigmaApiError(Exception):
    pass


class FigmaClient:
    def __init__(self) -> None:
        self._headers = {
            "X-Figma-Token": settings.figma_access_token
        }

    async def get_file(self, file_key: str) -> dict[str, Any]:
        url = f"{FIGMA_API_BASE_URL}/files/{file_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)

        if response.status_code == 401:
            raise FigmaApiError("Invalid Figma access token")

        if response.status_code == 404:
            raise FigmaApiError("Figma file not found")

        if response.status_code >= 400:
            raise FigmaApiError(
                f"Figma API error: {response.status_code}"
            )

        return response.json()
