from fastapi import APIRouter, HTTPException

from app.schemas.mintburn import MintBurnStatsResponse
from app.services.mintburn import get_mintburn_stats

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/stats", response_model=MintBurnStatsResponse)
def get_stats_route() -> MintBurnStatsResponse:
    try:
        return get_mintburn_stats()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
