"""
Bootstrap del catalogo dmbUi a partire da uno showcase Kotlin.

Strategia:
- Cerca pattern noti di registrazione componenti nel sorgente Kotlin
  (Field(..., XxxField(...)), DxRiepilogoXxx(...), DxXxx(...))
- Per ogni nome canonico genera alias derivati (rimuovendo i suffissi
  'Field', 'View', 'Element', 'Row' e prefissi 'Dx', 'DxRiepilogo')
- Inferisce 'tags' base (input, riepilogo, button, ecc.)
- Tenta di estrarre i nomi degli argomenti nominali della prima istanziazione
  come 'properties' attese (best-effort, regex sull'argument list).
"""
from __future__ import annotations

import re
from pathlib import Path

from app.schemas.components import CatalogComponentCreate

# Field("id", XxxField(args...))
_FIELD_RE = re.compile(r"\bField\s*\(\s*\"[^\"]*\"\s*,\s*([A-Z][A-Za-z0-9_]*Field)\s*(?:\(([^()]*(?:\([^()]*\)[^()]*)*)\))?")
# Standalone Dx* / DxRiepilogo* class instantiations
_DX_RE = re.compile(r"\b(Dx[A-Z][A-Za-z0-9_]+)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)")
# Other *Field types referenced directly (e.g. GapViewField.newInstance, ButtonViewField(...))
_FIELD_DIRECT_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*Field)\s*\(")

_NAMED_ARG_RE = re.compile(r"\b([a-z][A-Za-z0-9_]*)\s*=")

_SKIP_NAMES = {
    "Field",
    "Section",
    "DxFormFieldFactory",
    "DxBottomSlidingPanelDialogFragment",
}


def _strip_suffix(name: str, suffixes: list[str]) -> str:
    for s in suffixes:
        if name.endswith(s) and len(name) > len(s):
            return name[: -len(s)]
    return name


def _strip_prefix(name: str, prefixes: list[str]) -> str:
    for p in prefixes:
        if name.startswith(p) and len(name) > len(p):
            return name[len(p):]
    return name


def _aliases_for(name: str) -> list[str]:
    aliases: set[str] = set()

    # Strip dx prefix
    no_dx = _strip_prefix(name, ["DxRiepilogo", "Dx"])
    aliases.add(no_dx)

    # Strip common suffixes
    base = _strip_suffix(no_dx, ["ViewField", "Field", "Element", "View", "Row"])
    if base and base != no_dx:
        aliases.add(base)

    # CamelCase tokens for fuzzy
    aliases.add(name)
    aliases.discard(name)  # canonical name not duplicated as alias
    return sorted(a for a in aliases if a)


def _tags_for(name: str) -> list[str]:
    n = name.lower()
    tags: list[str] = []
    if "riepilogo" in n:
        tags.append("riepilogo")
    if "button" in n or "pulsantiera" in n:
        tags.append("button")
    if "input" in n or "password" in n or "autocomplete" in n or "spinner" in n or "date" in n or "calendar" in n:
        tags.append("input")
    if "text" in n or "title" in n or "label" in n:
        tags.append("text")
    if "image" in n or "icon" in n:
        tags.append("image")
    if "toggle" in n or "checkbox" in n:
        tags.append("selection")
    if "disclaimer" in n or "tooltip" in n:
        tags.append("info")
    if "divider" in n or "gap" in n:
        tags.append("layout")
    return tags


def _extract_named_args(args_blob: str) -> list[str]:
    if not args_blob:
        return []
    # Remove parentheses content depth>0 to keep only the top-level signature args
    seen: list[str] = []
    for m in _NAMED_ARG_RE.finditer(args_blob):
        a = m.group(1)
        if a not in seen:
            seen.append(a)
    return seen


def parse_kotlin_showcase(source: str) -> dict[str, CatalogComponentCreate]:
    """
    Returns a dict canonical_name -> CatalogComponentCreate, deduped.
    """
    found: dict[str, CatalogComponentCreate] = {}

    def _register(name: str, args_blob: str = "") -> None:
        if name in _SKIP_NAMES:
            return
        if name in found:
            # enrich properties if we now have args
            if args_blob and not found[name].properties:
                props = _extract_named_args(args_blob)
                if props:
                    found[name].properties = props
            return
        found[name] = CatalogComponentCreate(
            name=name,
            description=f"Imported from showcaseUi.kt ({name})",
            aliases=_aliases_for(name),
            tags=_tags_for(name),
            properties=_extract_named_args(args_blob),
        )

    for m in _FIELD_RE.finditer(source):
        _register(m.group(1), m.group(2) or "")

    for m in _DX_RE.finditer(source):
        _register(m.group(1), m.group(2) or "")

    for m in _FIELD_DIRECT_RE.finditer(source):
        _register(m.group(1))

    return found


def bootstrap_from_kotlin_file(path: Path) -> list[CatalogComponentCreate]:
    text = path.read_text(encoding="utf-8")
    return list(parse_kotlin_showcase(text).values())

