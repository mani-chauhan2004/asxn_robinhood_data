from fastapi import APIRouter, HTTPException, Query
from app.services.tokenization import get_value_by_category
from app.schemas.tokenization import ValueByCategoryResponse, TimePeriod
from datetime import date

router = APIRouter(prefix="/tokenization", tags=["tokenization"])

@router.get("/value-by-category", response_model=ValueByCategoryResponse)
def get_value_by_category_route(
    period: TimePeriod | None = Query(TimePeriod.one_month),
    from_date: date | None = None,
    to_date: date | None = None,
) -> ValueByCategoryResponse:
    try:
        return get_value_by_category(period, from_date, to_date)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")