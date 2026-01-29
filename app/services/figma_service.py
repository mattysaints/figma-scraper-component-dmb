import re
from typing import Any
from urllib.parse import urlparse, parse_qs
from pydantic import HttpUrl

from app.services.figma_client import FigmaClient

# --- existing URL parsing function ---
FIGMA_FILE_KEY_REGEX = re.compile(r"/design/([^/]+)")


def parse_figma_url(figma_url: HttpUrl) -> tuple[str, str | None]:
    """
    Extracts file_key and optional node_id from a Figma URL.
    """
    url_str = str(figma_url)

    match = FIGMA_FILE_KEY_REGEX.search(url_str)
    if not match:
        raise ValueError("Invalid Figma design URL")

    file_key = match.group(1)

    parsed_url = urlparse(url_str)
    query_params = parse_qs(parsed_url.query)
    node_id = query_params.get("node-id", [None])[0]

    return file_key, node_id


# --- new function to fetch the file from Figma ---
async def fetch_figma_file(figma_url: HttpUrl) -> dict[str, Any]:
    """
    Given a Figma URL, fetch the file JSON from the Figma API.
    """
    file_key, _ = parse_figma_url(figma_url)

    client = FigmaClient()
    return await client.get_file(file_key)
