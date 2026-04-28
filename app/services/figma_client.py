import asyncio
import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.retry_utils import parse_retry_after
from app.services.retry_policy import decide_retry
from app.types.figma import FigmaFile


def _figma_error_body(response: httpx.Response) -> str:
    """Try to extract Figma's JSON error message ('err' or 'message')."""
    try:
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("err") or data.get("message") or data)
    except Exception:
        pass
    return response.text


class FigmaClient:
    def __init__(self) -> None:
        token = (settings.figma_access_token or "").strip().strip('"').strip("'")
        self._headers = {
            "X-Figma-Token": token,
        }
        self._token = token

    async def whoami(self) -> dict:
        """Validate the token. Returns user info if OK, raises 401/403 with details."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{settings.figma_api_url}/me", headers=self._headers)
        if r.status_code == 200:
            return r.json()
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Figma token check failed (GET /v1/me): {_figma_error_body(r)}",
        )

    async def get_file(self, file_key: str) -> FigmaFile:
        if not self._token:
            raise HTTPException(
                status_code=500,
                detail="FIGMA_ACCESS_TOKEN is empty. Set it in .env.",
            )
        url = f"{settings.figma_api_url}/files/{file_key}"

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

                if response.status_code in (
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_403_FORBIDDEN,
                ):
                    body = _figma_error_body(response)
                    # Try to discriminate token vs. file access
                    hint = ""
                    try:
                        me = await self.whoami()
                        # Token is valid -> the file itself is the problem
                        user = me.get("email") or me.get("handle") or "user"
                        hint = (
                            f" Token OK (authenticated as {user}). "
                            "The file is not accessible by this token: "
                            "make sure the token has the 'file_content:read' scope "
                            "and that your account has access to this Figma file "
                            "(open it in the browser while logged in with the SAME account "
                            "that generated the token)."
                        )
                    except HTTPException as token_err:
                        hint = (
                            " Token check also failed: "
                            f"{token_err.detail}. "
                            "Generate a new Personal Access Token at "
                            "https://www.figma.com/developers/api#access-tokens "
                            "with scopes 'file_content:read' and 'file_metadata:read'."
                        )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Figma API {response.status_code}: {body}.{hint}",
                    )

                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Figma API error: {_figma_error_body(response)}",
                )

        raise HTTPException(
            status_code=429,
            detail="Figma API rate limit exceeded after retries.",
        )
