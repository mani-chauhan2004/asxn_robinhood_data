from pydantic import BaseModel


class TopAsset(BaseModel):
    symbol: str
    name: str


class LargestAsset(BaseModel):
    symbol: str
    name: str
    value: float
    change_24h: float
    change_30d: float


class AssetsMetricsResponse(BaseModel):
    total_assets: int
    top_assets: list[TopAsset]
    total_value_tokenized: float
    tvl_change_24h: float
    tvl_change_30d: float
    largest_asset: LargestAsset
    categories: int
    category_names: list[str]
