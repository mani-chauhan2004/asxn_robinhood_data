from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.mintburn import MintBurnCategoryShareResponse
from app.schemas.tokenization import TimePeriod
from app.services.mintburn import get_mint_burn_category_share

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/category-share", response_model=MintBurnCategoryShareResponse)
def get_category_share_route(
    period:    TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None       = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date:   date | None       = Query(None, alias="to",   description="Custom end date (YYYY-MM-DD)"),
) -> MintBurnCategoryShareResponse:
    try:
        return get_mint_burn_category_share(
            period=period, from_date=from_date, to_date=to_date,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
