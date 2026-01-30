from fastapi import APIRouter

from app.schemas.figma import FigmaAnalyzeRequest
from app.schemas.styles import ExtractedStyles
from app.services.figma_service import fetch_target_node
from app.services.style_extractor import extract_styles

router = APIRouter(prefix="/figma", tags=["Figma"])


@router.post(
    "/analyze",
    response_model=ExtractedStyles,
)
async def analyze_figma_design(payload: FigmaAnalyzeRequest):
    target_node = await fetch_target_node(
        payload.figma_url,
        payload.use_node_id,
    )

    return extract_styles(target_node)
