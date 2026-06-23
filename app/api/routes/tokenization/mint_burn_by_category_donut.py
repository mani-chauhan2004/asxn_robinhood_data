from fastapi import APIRouter, HTTPException

from app.schemas.tokenization import MintBurnByCategoryDonutResponse
from app.services.tokenization import get_mint_burn_by_category_donut

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


@router.get("/mint-burn-by-category-donut", response_model=MintBurnByCategoryDonutResponse)
def mint_burn_by_category_donut_route() -> MintBurnByCategoryDonutResponse:
    try:
        return get_mint_burn_by_category_donut()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
