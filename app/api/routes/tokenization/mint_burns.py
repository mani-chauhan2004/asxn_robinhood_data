from datetime import date
from fastapi import APIRouter, HTTPException, Query
from app.schemas.tokenization import MintBurnResponse, TimePeriod
from app.services.tokenization import get_mint_burns

router = APIRouter(prefix="/tokenization", tags=["tokenization"])

@router.get("/mint-burns", response_model=MintBurnResponse)
async def get_tokenization_mint_burns(
    period:    TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None       = Query(None, alias="from", description="Custom start date (YYYY-MM-DD)"),
    to_date:   date | None       = Query(None, alias="to",   description="Custom end date (YYYY-MM-DD)"),
):
    try:
        return get_mint_burns(period=period, from_date=from_date, to_date=to_date)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")