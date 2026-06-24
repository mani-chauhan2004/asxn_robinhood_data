from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.mintburn import TokenVolumeResponse
from app.schemas.tokenization import TimePeriod
from app.services.mintburn import get_token_volume

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/volume-by-token", response_model=TokenVolumeResponse)
def get_token_volume_route(
    token_symbol: str | None     = Query(None, description="Token symbol (e.g. AAPL)"),
    all_assets:   bool           = Query(False, description="Aggregate across all tokens"),
    period:    TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None       = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date:   date | None       = Query(None, alias="to",   description="Custom end date (YYYY-MM-DD)"),
) -> TokenVolumeResponse:
    if not all_assets and not token_symbol:
        raise HTTPException(status_code=400, detail="Provide token_symbol or set all_assets=true")
    try:
        return get_token_volume(
            token_symbol=None if all_assets else token_symbol,
            period=period, from_date=from_date, to_date=to_date,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
