from enum import Enum

from pydantic import BaseModel

from app.schemas.tokenization import TimePeriod


class TokenMintBurn(BaseModel):
    mint_usd: float
    burn_usd: float


class MintBurnVolumeUsdPoint(BaseModel):
    date: str
    tokens: dict[str, TokenMintBurn]
    total_mint_usd: float
    total_burn_usd: float
    cumulative_mint_usd: float
    cumulative_burn_usd: float
    cumulative_net_usd: float


class MintBurnVolumeUsdResponse(BaseModel):
    data: list[MintBurnVolumeUsdPoint]
    total_mint_usd: float
    total_burn_usd: float
    total_net_usd: float
    period: TimePeriod | None
    earliest_date: str
    latest_date: str


class MintBurnToken(BaseModel):
    symbol: str
    name: str
    category: str


class MintBurnTokensResponse(BaseModel):
    tokens: list[MintBurnToken]
    total: int


class TokenVolumePoint(BaseModel):
    date: str
    mint_usd: float
    burn_usd: float
    net_usd: float
    cumulative_mint_usd: float
    cumulative_burn_usd: float
    cumulative_net_usd: float


class TokenVolumeResponse(BaseModel):
    token_symbol: str
    data: list[TokenVolumePoint]
    total_mint_usd: float
    total_burn_usd: float
    total_net_usd: float
    period: TimePeriod | None
    earliest_date: str
    latest_date: str


class MintBurnStatsResponse(BaseModel):
    cumulative_mint_usd: float
    cumulative_burn_usd: float
    cumulative_net_usd: float
    mint_24h_usd: float
    mint_24h_change_pct: float


class MintBurnCategorySharePoint(BaseModel):
    date: str
    mint_share_pct: dict[str, float]
    burn_share_pct: dict[str, float]


class MintBurnCategoryShareResponse(BaseModel):
    data: list[MintBurnCategorySharePoint]
    period: TimePeriod | None
    earliest_date: str
    latest_date: str
    categories: list[str]


class IssuanceFirehoseSortBy(str, Enum):
    timestamp = "timestamp"
    token_name = "token_name"
    symbol = "symbol"
    type = "type"
    amount = "amount"
    value_usd = "value_usd"
    category = "category"


class IssuanceFirehoseRow(BaseModel):
    timestamp: str
    token_name: str
    symbol: str
    type: str
    amount: float
    value_usd: float
    category: str
    tx_hash: str


class IssuanceFirehoseResponse(BaseModel):
    data: list[IssuanceFirehoseRow]
    categories: list[str]
    nextPage: int | None
    totalEvents: int
