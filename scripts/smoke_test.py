"""Smoke test: extraction + matching + Kotlin bootstrap parsing."""
import os
import sys
from pathlib import Path

os.environ.setdefault("FIGMA_ACCESS_TOKEN", "dummy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.component_extractor import extract_components
from app.services.component_matcher import match_components
from app.services.component_catalog import catalog
from app.services.catalog_bootstrap import bootstrap_from_kotlin_file


def fake_figma_doc():
    return {
        "id": "0:0", "type": "DOCUMENT", "name": "root",
        "children": [{
            "id": "1", "type": "CANVAS", "name": "Page 1",
            "children": [
                {"id": "2", "type": "INSTANCE", "name": "InputViewField",
                 "componentId": "C1",
                 "componentProperties": {
                     "label#1:0": {"type": "TEXT", "value": "Email"},
                     "disabled#1:1": {"type": "BOOLEAN", "value": False},
                 },
                 "absoluteBoundingBox": {"x": 0, "y": 0, "width": 320, "height": 40},
                 "children": [{"type": "TEXT", "characters": "Email"}]},
                {"id": "3", "type": "INSTANCE", "name": "Button/Primary",
                 "componentId": "C2",
                 "absoluteBoundingBox": {"x": 0, "y": 0, "width": 120, "height": 40},
                 "children": [{"type": "TEXT", "characters": "Submit"}]},
                {"id": "4", "type": "COMPONENT",
                 "name": "state=disabled, size=lg", "children": []},
                {"id": "5", "type": "INSTANCE",
                 "name": "DynamicLocalizeText", "componentId": "C3", "children": []},
                {"id": "6", "type": "INSTANCE",
                 "name": "TooltipView", "componentId": "C4", "children": []},
                {"id": "7", "type": "INSTANCE",
                 "name": "WeirdUnknownThing", "componentId": "C5", "children": []},
            ],
        }],
    }


def main():
    print("=" * 60)
    print("1) BOOTSTRAP CATALOG from showcaseUi.kt")
    print("=" * 60)
    showcase = ROOT / "app" / "dmbComponent" / "showcaseUi.kt"
    parsed = bootstrap_from_kotlin_file(showcase)
    print(f"Parsed {len(parsed)} components from Kotlin source.")

    # Wipe & re-import into the catalog
    for existing in catalog.list():
        catalog.delete(existing.name)
    for item in parsed:
        try:
            catalog.create(item)
        except ValueError:
            pass

    catalog_entries = catalog.list()
    print(f"Catalog now has {len(catalog_entries)} entries.\n")

    print("=" * 60)
    print("2) EXTRACT + MATCH from a fake Figma document")
    print("=" * 60)
    extracted = extract_components(fake_figma_doc())
    print(f"Extracted {len(extracted)} component nodes:")
    for e in extracted:
        print(f"  - {e.figma_type:14s} {e.figma_name!r}  variants={e.variants}  props={e.properties}")

    results = match_components(extracted, catalog_entries, threshold=0.6)
    print()
    for r in results:
        bm = r.best_match
        bm_str = f"{bm.dmbui_name} ({bm.confidence}, {bm.reason})" if bm else "—"
        print(f"  {r.extracted.figma_name!r:30s} matched={r.matched}  best={bm_str}")
        for s in r.suggestions:
            print(f"      suggest: {s.dmbui_name:35s} {s.confidence}  {s.reason}")


if __name__ == "__main__":
    main()



