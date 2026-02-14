import re
from typing import Optional
from urllib.parse import urlparse, parse_qs
from pydantic import HttpUrl

from app.services.figma_client import FigmaClient
from app.types.figma import FigmaNode

FIGMA_FILE_KEY_REGEX = re.compile(r"/(?:file|design)/([^/]+)")

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

    if node_id is not None:
        node_id = node_id.replace("-", ":")

    return file_key, node_id


async def fetch_target_node(
    figma_url: HttpUrl,
    use_node_id: bool,
) -> FigmaNode:
    file_key, node_id = parse_figma_url(figma_url)

    client = FigmaClient()
    file_data = await client.get_file(file_key)

    document = file_data.get("document")
    if not isinstance(document, dict):
        raise ValueError("Invalid Figma file structure")

    if use_node_id:
        if node_id is None:
            raise ValueError("use_node_id=true but no node-id found in URL")

        target = find_node_by_id(document, node_id)
        if target is None:
            raise ValueError(f"Node with id '{node_id}' not found")

        return target

    return document


def find_node_by_id(
    node: FigmaNode,
    node_id: str,
) -> Optional[FigmaNode]:
    if node.get("id") == node_id:
        return node

    children = node.get("children")
    if isinstance(children, list):
        for child in children:
            result = find_node_by_id(child, node_id)
            if result is not None:
                return result

    return None