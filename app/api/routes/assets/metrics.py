import json

from fastapi import APIRouter, HTTPException

from app.core.paths import ASSETS_METRICS
from app.schemas.assets import AssetsMetricsResponse

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.get("/metrics", response_model=AssetsMetricsResponse)
async def get_assets_metrics():
    if not ASSETS_METRICS.exists():
        raise HTTPException(
            status_code=503,
            detail="Metrics not yet available. Run scripts/cache_dune_queries.py first.",
        )
    return json.loads(ASSETS_METRICS.read_text())
