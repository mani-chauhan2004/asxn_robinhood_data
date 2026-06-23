from app.api.routes.assets import explorer as assets_explorer
from app.api.routes.assets import metrics as assets_metrics
from app.api.routes.dune import queries as dune_queries
from app.api.routes.tokenization import tvt as tokenization_tvt
from fastapi import APIRouter

router = APIRouter()
router.include_router(dune_queries.router)
router.include_router(assets_metrics.router)
router.include_router(assets_explorer.router)
router.include_router(tokenization_tvt.router)