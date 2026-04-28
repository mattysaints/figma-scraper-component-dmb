from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.components import (
    AliasAddRequest,
    CatalogComponent,
    CatalogComponentCreate,
    CatalogComponentUpdate,
)
from app.services.catalog_bootstrap import bootstrap_from_kotlin_file
from app.services.component_catalog import catalog

router = APIRouter(prefix="/catalog/components", tags=["Catalog"])

_DEFAULT_SHOWCASE = (
    Path(__file__).resolve().parent.parent.parent
    / "dmbComponent"
    / "showcaseUi.kt"
)


class BootstrapRequest(BaseModel):
    source_path: str | None = Field(
        default=None,
        description="Absolute path to the Kotlin showcase file. Defaults to app/dmbComponent/showcaseUi.kt",
    )
    mode: str = Field(default="merge", pattern="^(merge|replace)$")


class BootstrapResponse(BaseModel):
    created: list[str]
    updated: list[str]
    skipped: list[str]
    total: int


# ---- Static routes BEFORE dynamic /{name} routes ----

@router.get("", response_model=list[CatalogComponent])
def list_components() -> list[CatalogComponent]:
    return catalog.list()


@router.post("", response_model=CatalogComponent, status_code=status.HTTP_201_CREATED)
def create_component(payload: CatalogComponentCreate) -> CatalogComponent:
    try:
        return catalog.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/bootstrap", response_model="BootstrapResponse")
def bootstrap_catalog(payload: BootstrapRequest | None = None) -> BootstrapResponse:
    """
    Populate the dmbUi catalog by parsing a Kotlin showcase source file.

    - mode='merge'  : add new components, update properties if missing on existing ones
    - mode='replace': wipe the catalog and re-import from scratch
    """
    payload = payload or BootstrapRequest()
    src = Path(payload.source_path) if payload.source_path else _DEFAULT_SHOWCASE
    if not src.exists():
        raise HTTPException(status_code=404, detail=f"Source file not found: {src}")

    parsed = bootstrap_from_kotlin_file(src)

    created: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    if payload.mode == "replace":
        for existing in catalog.list():
            catalog.delete(existing.name)

    existing_names = {c.name.lower() for c in catalog.list()}

    for item in parsed:
        if item.name.lower() in existing_names:
            try:
                current = catalog.get(item.name)
                if current is None:
                    skipped.append(item.name)
                    continue
                # Merge aliases + properties; do not overwrite existing values
                merged_aliases = sorted(set(current.aliases) | set(item.aliases))
                merged_props = current.properties or item.properties
                merged_tags = sorted(set(current.tags) | set(item.tags))
                catalog.update(
                    item.name,
                    CatalogComponentUpdate(
                        aliases=merged_aliases,
                        properties=merged_props,
                        tags=merged_tags,
                    ),
                )
                updated.append(item.name)
            except KeyError:
                skipped.append(item.name)
        else:
            try:
                catalog.create(item)
                created.append(item.name)
            except ValueError:
                skipped.append(item.name)

    return BootstrapResponse(
        created=sorted(created),
        updated=sorted(updated),
        skipped=sorted(skipped),
        total=len(parsed),
    )


# ---- Dynamic /{name} routes (must come AFTER static ones) ----

@router.get("/{name}", response_model=CatalogComponent)
def get_component(name: str) -> CatalogComponent:
    item = catalog.get(name)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Component '{name}' not found")
    return item


@router.put("/{name}", response_model=CatalogComponent)
def update_component(name: str, payload: CatalogComponentUpdate) -> CatalogComponent:
    try:
        return catalog.update(name, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(name: str) -> None:
    try:
        catalog.delete(name)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{name}/aliases", response_model=CatalogComponent)
def add_alias(name: str, payload: AliasAddRequest) -> CatalogComponent:
    try:
        return catalog.add_alias(name, payload.alias)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))




