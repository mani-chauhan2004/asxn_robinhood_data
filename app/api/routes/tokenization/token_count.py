from fastapi import APIRouter, Query
from datetime import date
from fastapi import HTTPException
from app.schemas.tokenization import AssetsTokenizedOverTimeResponse, TimePeriod
from app.services.tokenization import get_assets_tokenized_over_time

router = APIRouter(prefix="/tokenization", tags=["tokenization"])

@router.get("/token-count", response_model=AssetsTokenizedOverTimeResponse)
async def get_token_count(
    period: TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, alias="to", description="Custom end date (YYYY-MM-DD)"),
):
    try:
        return get_assets_tokenized_over_time(period=period, from_date=from_date, to_date=to_date)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")