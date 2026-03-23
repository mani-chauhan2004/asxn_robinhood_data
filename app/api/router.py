from app.api.routes.dune import queries as dune_queries
from fastapi import APIRouter

router = APIRouter()
router.include_router(dune_queries.router)