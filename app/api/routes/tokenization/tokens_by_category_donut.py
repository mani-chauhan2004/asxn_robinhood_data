from fastapi import APIRouter, HTTPException

from app.schemas.tokenization import TokensByCategoryDonutResponse
from app.services.tokenization import get_tokens_by_category_donut

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


@router.get("/tokens-by-category-donut", response_model=TokensByCategoryDonutResponse)
def tokens_by_category_donut_route() -> TokensByCategoryDonutResponse:
    try:
        return get_tokens_by_category_donut()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
