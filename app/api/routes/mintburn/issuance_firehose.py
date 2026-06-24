from fastapi import APIRouter, HTTPException, Query

from app.schemas.mintburn import IssuanceFirehoseResponse, IssuanceFirehoseSortBy
from app.services.issuance_firehose import get_issuance_firehose

router = APIRouter(prefix="/mintburn", tags=["mintburn"])


@router.get("/issuance-firehose", response_model=IssuanceFirehoseResponse)
def get_issuance_firehose_route(
    page:         int                     = Query(1, ge=1),
    limit:        int                     = Query(50, ge=1, le=200),
    search:       str                     = Query("", description="Filter by token name or symbol"),
    category:     str | None              = Query(None, description="Filter by category"),
    event_type:   str | None              = Query(None, description="Filter by MINT or BURN"),
    token_symbol: str | None              = Query(None, description="Filter by token symbol"),
    sort_by:      IssuanceFirehoseSortBy  = Query(IssuanceFirehoseSortBy.timestamp),
    sort_order:   str                     = Query("desc", description="asc or desc"),
) -> IssuanceFirehoseResponse:
    try:
        return get_issuance_firehose(
            page=page,
            limit=limit,
            search=search,
            category=category,
            event_type=event_type.upper() if event_type else None,
            token_symbol=token_symbol,
            sort_by=sort_by.value,
            sort_order=sort_order,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Data not available: {e.filename}")
