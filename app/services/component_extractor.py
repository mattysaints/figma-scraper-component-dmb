from __future__ import annotations

from typing import Any, Optional

from app.schemas.components import ExtractedComponent

_TARGET_TYPES = {"COMPONENT", "COMPONENT_SET", "INSTANCE"}


def _parse_variants_from_name(name: str) -> dict[str, str]:
    """
    Figma variant nodes are often named like 'state=disabled, size=lg'.
    """
    variants: dict[str, str] = {}
    if "=" not in name:
        return variants
    parts = [p.strip() for p in name.split(",")]
    for p in parts:
        if "=" in p:
            k, _, v = p.partition("=")
            k, v = k.strip(), v.strip()
            if k and v:
                variants[k] = v
    return variants


def _coerce_property_value(value: Any) -> str:
    if isinstance(value, dict) and "value" in value:
        value = value["value"]
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _extract_properties(node: dict[str, Any]) -> dict[str, str]:
    raw = node.get("componentProperties")
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for k, v in raw.items():
        clean_key = k.split("#", 1)[0]
        result[clean_key] = _coerce_property_value(v)
    return result


def _extract_text_content(node: dict[str, Any]) -> Optional[str]:
    if node.get("type") == "TEXT":
        chars = node.get("characters")
        if isinstance(chars, str):
            return chars
    children = node.get("children")
    if isinstance(children, list):
        for c in children:
            if isinstance(c, dict):
                t = _extract_text_content(c)
                if t:
                    return t
    return None


def _bbox(node: dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
    box = node.get("absoluteBoundingBox")
    if isinstance(box, dict):
        return box.get("width"), box.get("height")
    return None, None


def _walk(node: dict[str, Any], out: list[ExtractedComponent]) -> None:
    ntype = node.get("type")
    if ntype in _TARGET_TYPES:
        width, height = _bbox(node)
        children = node.get("children") or []
        out.append(
            ExtractedComponent(
                figma_node_id=str(node.get("id", "")),
                figma_name=str(node.get("name", "")),
                figma_type=str(ntype),
                component_id=node.get("componentId"),
                variants=_parse_variants_from_name(str(node.get("name", ""))),
                properties=_extract_properties(node),
                text_content=_extract_text_content(node),
                width=width,
                height=height,
                children_count=len(children) if isinstance(children, list) else 0,
            )
        )
        # Do NOT recurse into INSTANCE (its internals are component children we don't need to re-list)
        if ntype == "INSTANCE":
            return

    children = node.get("children")
    if isinstance(children, list):
        for c in children:
            if isinstance(c, dict):
                _walk(c, out)


def extract_components(document: dict[str, Any]) -> list[ExtractedComponent]:
    out: list[ExtractedComponent] = []
    _walk(document, out)
    return out

