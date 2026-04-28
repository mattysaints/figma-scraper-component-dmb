from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


# ---------- Catalog (dmbUi) ----------

class CatalogComponent(BaseModel):
    """A component available in the dmbUi repository."""
    name: str = Field(..., description="Canonical dmbUi component name (e.g. DxDynamicLocalizeTextView)")
    description: Optional[str] = None
    aliases: list[str] = Field(
        default_factory=list,
        description="Known Figma names / synonyms that map to this component",
    )
    tags: list[str] = Field(default_factory=list)
    properties: list[str] = Field(
        default_factory=list,
        description="Expected configurable properties (e.g. ['text','placeholder','disabled'])",
    )


class CatalogComponentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    properties: list[str] = Field(default_factory=list)


class CatalogComponentUpdate(BaseModel):
    description: Optional[str] = None
    aliases: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    properties: Optional[list[str]] = None


class AliasAddRequest(BaseModel):
    alias: str


# ---------- Figma extracted components ----------

class ExtractedComponent(BaseModel):
    figma_node_id: str
    figma_name: str
    figma_type: str = Field(..., description="COMPONENT | COMPONENT_SET | INSTANCE | FRAME")
    component_id: Optional[str] = Field(
        default=None,
        description="For INSTANCE nodes, the referenced componentId",
    )
    variants: dict[str, str] = Field(
        default_factory=dict,
        description="Variant properties (e.g. {'state':'disabled','size':'lg'})",
    )
    properties: dict[str, str] = Field(
        default_factory=dict,
        description="componentProperties values (text, boolean, instance swap, ...)",
    )
    text_content: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    children_count: int = 0


class ComponentMatch(BaseModel):
    dmbui_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str


class MatchedComponent(BaseModel):
    extracted: ExtractedComponent
    best_match: Optional[ComponentMatch] = None
    suggestions: list[ComponentMatch] = Field(default_factory=list)
    matched: bool = False


class ComponentAnalyzeRequest(BaseModel):
    figma_url: HttpUrl
    use_node_id: bool = False
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    include_unmatched: bool = True
    only_instances: bool = Field(
        default=True,
        description="If true, return only INSTANCE/COMPONENT nodes (skip raw FRAME)",
    )


class ComponentAnalyzeResponse(BaseModel):
    file_key: str
    node_id: Optional[str]
    total_extracted: int
    matched_count: int
    unmatched_count: int
    components: list[MatchedComponent]

