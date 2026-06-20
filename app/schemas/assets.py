from pydantic import BaseModel
from enum import Enum


class TopAsset(BaseModel):
    symbol: str
    name: str
    logo_url: str = ""


class LargestAsset(BaseModel):
    symbol: str
    name: str
    value: float
    change_24h: float
    change_30d: float


class SortBy(str, Enum):
    name      = "name"
    symbol    = "symbol"
    value     = "value"
    shares    = "shares"
    price     = "price"
    pct_total = "pct_total"
    change_1d  = "change_1d"
    change_7d  = "change_7d"
    change_30d = "change_30d"


class SortOrder(str, Enum):
    asc  = "asc"
    desc = "desc"


class AssetRow(BaseModel):
    symbol:    str
    name:      str
    logo_url:  str
    category:  str
    price:     float
    shares:    float
    value:     float
    pct_total: float
    change_1d:  float | None
    change_7d:  float | None
    change_30d: float | None


class AssetExplorerResponse(BaseModel):
    data:        list[AssetRow]
    categories:  list[str]
    hasNextPage: int | None


class AssetsMetricsResponse(BaseModel):
    total_assets: int
    top_assets: list[TopAsset]
    total_value_tokenized: float
    tvl_change_24h: float
    tvl_change_30d: float
    largest_asset: LargestAsset
    categories: int
    category_names: list[str]
