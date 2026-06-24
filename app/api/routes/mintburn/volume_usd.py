from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.mintburn import MintBurnVolumeUsdResponse
from app.schemas.tokenization import TimePeriod
from app.services.mintburn import get_mint_burn_volume_usd

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/volume-usd", response_model=MintBurnVolumeUsdResponse)
def get_volume_usd_route(
    period:    TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None       = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date:   date | None       = Query(None, alias="to",   description="Custom end date (YYYY-MM-DD)"),
    token_symbol: str | None     = Query(None, description="Filter by token symbol (e.g. AAPL)"),
) -> MintBurnVolumeUsdResponse:
    try:
        return get_mint_burn_volume_usd(
            period=period, from_date=from_date, to_date=to_date, token_symbol=token_symbol,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
