import asyncio
import json
import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.components import (
    ComponentAnalyzeRequest,
    ComponentAnalyzeResponse,
)
from app.schemas.figma import FigmaAnalyzeRequest
from app.schemas.styles import ExtractedStyles
from app.services.component_catalog import catalog
from app.services.component_extractor import extract_components
from app.services.component_matcher import match_components
from app.services.figma_client import FigmaClient
from app.services.figma_extractor import extract_styles
from app.services.figma_service import fetch_target_node, parse_figma_url

router = APIRouter(prefix="/figma", tags=["Figma"])
log = logging.getLogger("app.figma")


@router.get("/whoami")
async def whoami() -> dict:
    """Diagnostic endpoint: validate the configured FIGMA_ACCESS_TOKEN."""
    return await FigmaClient().whoami()


@router.post(
    "/analyze",
    response_model=ExtractedStyles,
)
async def analyze_figma_design(payload: FigmaAnalyzeRequest):
    t0 = time.perf_counter()
    log.info("[/analyze] fetching Figma node from %s", payload.figma_url)
    target_node = await fetch_target_node(payload.figma_url, payload.use_node_id)
    log.info("[/analyze] fetched in %.2fs, extracting styles…", time.perf_counter() - t0)
    result = extract_styles(target_node)
    log.info(
        "[/analyze] done in %.2fs (colors=%d, text_styles=%d)",
        time.perf_counter() - t0, len(result.colors), len(result.text_styles),
    )
    return result


@router.post(
    "/components",
    response_model=ComponentAnalyzeResponse,
)
async def analyze_figma_components(payload: ComponentAnalyzeRequest) -> ComponentAnalyzeResponse:
    """
    Extract Figma components/instances and match them against the dmbUi catalog.
    """
    t0 = time.perf_counter()
    log.info("[/components] step=fetch_figma url=%s use_node_id=%s", payload.figma_url, payload.use_node_id)
    target_node = await fetch_target_node(payload.figma_url, payload.use_node_id)
    file_key, node_id = parse_figma_url(payload.figma_url)
    t_fetch = time.perf_counter() - t0

    log.info("[/components] step=extract")
    t1 = time.perf_counter()
    extracted = extract_components(target_node)
    if payload.only_instances:
        extracted = [e for e in extracted if e.figma_type in {"INSTANCE", "COMPONENT", "COMPONENT_SET"}]
    t_extract = time.perf_counter() - t1
    log.info("[/components] extracted=%d in %.2fs", len(extracted), t_extract)

    log.info("[/components] step=match")
    t2 = time.perf_counter()
    catalog_entries = catalog.list()
    matched = match_components(
        extracted, catalog_entries, threshold=payload.confidence_threshold,
    )
    t_match = time.perf_counter() - t2

    if not payload.include_unmatched:
        matched = [m for m in matched if m.matched]

    matched_count = sum(1 for m in matched if m.matched)
    log.info(
        "[/components] done total=%d matched=%d unmatched=%d "
        "(fetch=%.2fs extract=%.2fs match=%.2fs total=%.2fs)",
        len(matched), matched_count, len(matched) - matched_count,
        t_fetch, t_extract, t_match, time.perf_counter() - t0,
    )
    return ComponentAnalyzeResponse(
        file_key=file_key,
        node_id=node_id if payload.use_node_id else None,
        total_extracted=len(matched),
        matched_count=matched_count,
        unmatched_count=len(matched) - matched_count,
        components=matched,
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/components/stream")
async def analyze_figma_components_stream(payload: ComponentAnalyzeRequest) -> StreamingResponse:
    """
    Same as /components, but streams progress updates via Server-Sent Events.

    Events:
      - phase: {"phase": "fetch|extract|match|done", "message": "...", "elapsed": <s>}
      - progress: {"current": int, "total": int, "label": str}
      - result: <full ComponentAnalyzeResponse JSON>
      - error: {"message": str}
    """
    async def gen() -> AsyncIterator[str]:
        try:
            t0 = time.perf_counter()
            yield _sse("phase", {"phase": "fetch", "message": "Contacting Figma…"})
            await asyncio.sleep(0)  # flush
            target_node = await fetch_target_node(payload.figma_url, payload.use_node_id)
            file_key, node_id = parse_figma_url(payload.figma_url)
            yield _sse("phase", {
                "phase": "extract",
                "message": "Extracting components from the document…",
                "elapsed": round(time.perf_counter() - t0, 2),
            })
            await asyncio.sleep(0)

            extracted = extract_components(target_node)
            if payload.only_instances:
                extracted = [e for e in extracted if e.figma_type in {"INSTANCE", "COMPONENT", "COMPONENT_SET"}]
            yield _sse("progress", {"current": len(extracted), "total": len(extracted), "label": "extracted"})

            yield _sse("phase", {
                "phase": "match",
                "message": f"Matching {len(extracted)} components against dmbUi catalog…",
                "elapsed": round(time.perf_counter() - t0, 2),
            })
            await asyncio.sleep(0)

            catalog_entries = catalog.list()
            matched = match_components(extracted, catalog_entries, threshold=payload.confidence_threshold)
            if not payload.include_unmatched:
                matched = [m for m in matched if m.matched]

            matched_count = sum(1 for m in matched if m.matched)
            response = ComponentAnalyzeResponse(
                file_key=file_key,
                node_id=node_id if payload.use_node_id else None,
                total_extracted=len(matched),
                matched_count=matched_count,
                unmatched_count=len(matched) - matched_count,
                components=matched,
            )
            yield _sse("phase", {
                "phase": "done",
                "message": "Analysis complete.",
                "elapsed": round(time.perf_counter() - t0, 2),
                "matched": matched_count,
                "unmatched": len(matched) - matched_count,
                "total": len(matched),
            })
            yield _sse("result", json.loads(response.model_dump_json()))
        except Exception as e:  # noqa: BLE001
            log.exception("stream analyze failed")
            yield _sse("error", {"message": f"{e.__class__.__name__}: {e}"})

    return StreamingResponse(gen(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


