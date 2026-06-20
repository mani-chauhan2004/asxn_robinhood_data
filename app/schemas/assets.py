from pydantic import BaseModel


class LargestAsset(BaseModel):
    symbol: str
    name: str
    value: float


class AssetsMetricsResponse(BaseModel):
    total_assets: int
    total_value_tokenized: float
    largest_asset: LargestAsset
    categories: int
