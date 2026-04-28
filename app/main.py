from pathlib import Path
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.figma import router as figma_router
from app.api.v1.catalog import router as catalog_router

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.environment == "development" else None,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log full traceback and return it (in dev) for easier debugging."""
    tb = traceback.format_exc()
    logger.error("Unhandled exception on %s %s\n%s", request.method, request.url.path, tb)
    payload = {
        "error": exc.__class__.__name__,
        "message": str(exc) or "Internal Server Error",
    }
    if settings.environment == "development":
        payload["traceback"] = tb.splitlines()[-12:]  # last 12 lines
    return JSONResponse(status_code=500, content=payload)


app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(figma_router, prefix=settings.api_v1_prefix)
app.include_router(catalog_router, prefix=settings.api_v1_prefix)

# Static UI
_STATIC_DIR = Path(__file__).resolve().parent / "static"
if _STATIC_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(_STATIC_DIR), html=True), name="ui")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui/")

