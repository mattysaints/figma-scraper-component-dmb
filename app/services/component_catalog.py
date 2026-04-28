from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional

from app.schemas.components import (
    CatalogComponent,
    CatalogComponentCreate,
    CatalogComponentUpdate,
)

_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "dmbui_catalog.json"
_LOCK = threading.RLock()


def _ensure_file() -> None:
    if not _CATALOG_PATH.exists():
        _CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CATALOG_PATH.write_text("[]", encoding="utf-8")


def _load_raw() -> list[dict]:
    _ensure_file()
    with _CATALOG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Catalog file must be a JSON array")
    return data


def _save_raw(items: list[dict]) -> None:
    _CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _CATALOG_PATH.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


class ComponentCatalog:
    """JSON-backed catalog of dmbUi components."""

    def list(self) -> list[CatalogComponent]:
        with _LOCK:
            return [CatalogComponent(**item) for item in _load_raw()]

    def get(self, name: str) -> Optional[CatalogComponent]:
        with _LOCK:
            for item in _load_raw():
                if item["name"].lower() == name.lower():
                    return CatalogComponent(**item)
        return None

    def create(self, payload: CatalogComponentCreate) -> CatalogComponent:
        with _LOCK:
            items = _load_raw()
            if any(i["name"].lower() == payload.name.lower() for i in items):
                raise ValueError(f"Component '{payload.name}' already exists")
            comp = CatalogComponent(**payload.model_dump())
            items.append(comp.model_dump())
            _save_raw(items)
            return comp

    def update(self, name: str, payload: CatalogComponentUpdate) -> CatalogComponent:
        with _LOCK:
            items = _load_raw()
            for idx, item in enumerate(items):
                if item["name"].lower() == name.lower():
                    updated = {**item}
                    for k, v in payload.model_dump(exclude_unset=True).items():
                        if v is not None:
                            updated[k] = v
                    items[idx] = updated
                    _save_raw(items)
                    return CatalogComponent(**updated)
            raise KeyError(f"Component '{name}' not found")

    def delete(self, name: str) -> None:
        with _LOCK:
            items = _load_raw()
            new_items = [i for i in items if i["name"].lower() != name.lower()]
            if len(new_items) == len(items):
                raise KeyError(f"Component '{name}' not found")
            _save_raw(new_items)

    def add_alias(self, name: str, alias: str) -> CatalogComponent:
        with _LOCK:
            items = _load_raw()
            for idx, item in enumerate(items):
                if item["name"].lower() == name.lower():
                    aliases: list[str] = list(item.get("aliases", []))
                    if alias and alias not in aliases:
                        aliases.append(alias)
                    item["aliases"] = aliases
                    items[idx] = item
                    _save_raw(items)
                    return CatalogComponent(**item)
            raise KeyError(f"Component '{name}' not found")


catalog = ComponentCatalog()

