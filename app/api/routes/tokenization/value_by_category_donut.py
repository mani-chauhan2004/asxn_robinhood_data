from fastapi import APIRouter, HTTPException

from app.schemas.tokenization import ValueByCategoryDonutResponse
from app.services.tokenization import get_value_by_category_donut

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


@router.get("/value-by-category-donut", response_model=ValueByCategoryDonutResponse)
def value_by_category_donut_route() -> ValueByCategoryDonutResponse:
    try:
        return get_value_by_category_donut()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
