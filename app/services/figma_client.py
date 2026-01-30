import asyncio
import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.retry_utils import parse_retry_after
from app.services.retry_policy import decide_retry
from app.types.figma import FigmaFile


class FigmaClient:
    def __init__(self) -> None:
        self._headers = {
            "X-Figma-Token": settings.figma_access_token,
        }

    async def get_file(self, file_key: str) -> FigmaFile:
        url = f"https://api.figma.com/v1/files/{file_key}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                response = await client.get(url, headers=self._headers)

                if response.status_code == status.HTTP_200_OK:
                    return response.json()

                if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    retry_after = parse_retry_after(
                        response.headers.get("Retry-After")
                    )

                    decision = decide_retry(retry_after, attempt)

                    if not decision.should_retry:
                        raise HTTPException(
                            status_code=429,
                            detail=(
                                "Figma API rate limit exceeded. "
                                f"Retry after {decision.wait_seconds} seconds."
                            ),
                            headers={
                                "Retry-After": str(decision.wait_seconds)
                            },
                        )

                    await asyncio.sleep(decision.wait_seconds)
                    continue

                if response.status_code == status.HTTP_403_FORBIDDEN:
                    raise HTTPException(
                        status_code=403,
                        detail="Figma API access denied. Check your token.",
                    )

                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Figma API error: {response.text}",
                )

        raise HTTPException(
            status_code=429,
            detail="Figma API rate limit exceeded after retries.",
        )
