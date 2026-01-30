from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.figma import router as figma_router

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.environment == "development" else None
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(figma_router, prefix=settings.api_v1_prefix)
