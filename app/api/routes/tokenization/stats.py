from fastapi import APIRouter, HTTPException

from app.schemas.tokenization import TokenizationStatsResponse
from app.services.tokenization import get_tokenization_stats

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


@router.get("/stats", response_model=TokenizationStatsResponse)
def get_stats_route() -> TokenizationStatsResponse:
    try:
        return get_tokenization_stats()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
