from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.tokenization import TimePeriod, TVTResponse
from app.services.tokenization import get_tvt

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


@router.get("/total-value-tokenized-over-time", response_model=TVTResponse)
async def get_tokenization_tvt(
    period:    TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None       = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date:   date | None       = Query(None, alias="to",   description="Custom end date (YYYY-MM-DD)"),
):
    try:
        return get_tvt(period=period, from_date=from_date, to_date=to_date)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
