from typing import Optional

from app.types.figma import FigmaNode


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
