from datetime import date
from enum import Enum
from pydantic import BaseModel


class TimePeriod(str, Enum):
    one_day       = "1D"
    seven_days    = "7D"
    one_month     = "1M"
    three_months  = "3M"
    one_year      = "1Y"
    all           = "ALL"


class TVTPoint(BaseModel):
    date:  str
    value: float


class TVTResponse(BaseModel):
    data:           list[TVTPoint]
    current_value:  float
    period:         TimePeriod | None
    earliest_date:  str
    latest_date:    str

class MintBurnPoint(BaseModel):
    date:  str
    mint:  float
    burn:  float
    total: float
    cumulative_total:float

class MintBurnResponse(BaseModel):
    data:           list[MintBurnPoint]
    total_mint:     float
    total_burn:     float
    total_net:      float
    last24h_mint:   float
    last24h_burn:   float
    last24h_net:    float
    last_30d_mint:  float
    last_30d_burn:  float
    last_30d_net:   float
    period:         TimePeriod | None
    earliest_date:  str
    latest_date:    str
    
class AssetsTokenizedOverTimePoint(BaseModel):
    date:  str
    count: float
    cumulative_count: float
    current_day_tokenized: list[str]

class AssetsTokenizedOverTimeResponse(BaseModel):
    data:           list[AssetsTokenizedOverTimePoint]
    current_count:  float
    total_count:    float
    period:         TimePeriod | None
    earliest_date:  str
    latest_date:    str