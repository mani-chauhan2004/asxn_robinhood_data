from fastapi import APIRouter, HTTPException, Query

from app.api.routes.assets.service import get_explorer_data
from app.schemas.assets import AssetExplorerResponse, Category, SortBy, SortOrder

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.get("/explorer", response_model=AssetExplorerResponse)
async def get_asset_explorer(
    page:       int       = Query(1,    ge=1),
    limit:      int       = Query(50,   ge=1, le=200),
    search:     str       = Query("",   description="Filter by name or symbol"),
    category:   Category | None = Query(None),
    min_value:  float     = Query(0.0,  ge=0, description="Minimum tokenized value in USD"),
    sort_by:    SortBy    = Query(SortBy.value),
    sort_order: SortOrder = Query(SortOrder.desc),
):
    try:
        return get_explorer_data(
            page=page,
            limit=limit,
            search=search,
            category=category.value if category else None,
            min_value=min_value,
            sort_by=sort_by.value,
            sort_order=sort_order.value,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Data not yet available. Run scripts/cache_dune_queries.py first.",
        )
