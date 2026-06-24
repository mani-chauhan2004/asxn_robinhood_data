from fastapi import APIRouter, HTTPException

from app.schemas.mintburn import MintBurnTokensResponse
from app.services.mintburn import get_mintburn_tokens

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/tokens", response_model=MintBurnTokensResponse)
def get_tokens_route() -> MintBurnTokensResponse:
    try:
        return get_mintburn_tokens()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
