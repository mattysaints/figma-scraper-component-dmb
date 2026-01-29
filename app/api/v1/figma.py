from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.schemas.figma import (
    FigmaAnalyzeRequest,
)
from app.services.figma_service import fetch_figma_file
from app.services.figma_client import FigmaApiError

router = APIRouter(prefix="/figma", tags=["Figma"])


@router.post("/analyze")
async def analyze_figma_design(payload: FigmaAnalyzeRequest) -> dict[str, Any]:
    try:
        figma_file = await fetch_figma_file(payload.figma_url)
    except FigmaApiError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # TEMP: return raw data (we'll extract styles next)
    return {
        "name": figma_file.get("name"),
        "lastModified": figma_file.get("lastModified"),
        "documentType": figma_file.get("document", {}).get("type"),
    }
