import json
from collections import defaultdict
from datetime import date, timedelta

from app.core.paths import DATA_DIR
from app.schemas.tokenization import MintBurnPoint, MintBurnResponse, TimePeriod, TVTPoint, TVTResponse

_PERIOD_DELTAS = {
    TimePeriod.one_day:      timedelta(days=1),
    TimePeriod.seven_days:   timedelta(days=7),
    TimePeriod.one_month:    timedelta(days=30),
    TimePeriod.three_months: timedelta(days=90),
    TimePeriod.one_year:     timedelta(days=365),
}


def get_tvt(
    period:    TimePeriod | None,
    from_date: date | None,
    to_date:   date | None,
) -> TVTResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    all_days = sorted({r["day"] for r in dm_rows})
    earliest = all_days[0] if all_days else date.today().isoformat()
    latest   = all_days[-1] if all_days else date.today().isoformat()

    end   = to_date.isoformat()   if to_date   else latest
    if from_date:
        start = from_date.isoformat()
    elif period and period != TimePeriod.all:
        start = (date.fromisoformat(end) - _PERIOD_DELTAS[period]).isoformat()
    else:
        start = earliest

    tvt_by_day: dict[str, float] = defaultdict(float)
    for r in dm_rows:
        day = r["day"]
        if not (start <= day <= end):
            continue
        price = price_map.get(r["token_symbol"], 0.0)
        tvt_by_day[day] += r["cumulative_tvl"] * price

    points = [
        TVTPoint(date=day, value=round(tvt_by_day[day], 2))
        for day in sorted(tvt_by_day)
    ]

    return TVTResponse(
        data=points,
        current_value=points[-1].value if points else 0.0,
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )
    
def get_mint_burns(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> MintBurnResponse: 
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    all_days = sorted({r["day"] for r in dm_rows})
    earliest = all_days[0] if all_days else date.today().isoformat()
    latest   = all_days[-1] if all_days else date.today().isoformat()
    
    end   = to_date.isoformat()   if to_date   else latest
    if from_date:
        start = from_date.isoformat()
    elif period and period != TimePeriod.all:
        start = (date.fromisoformat(end) - _PERIOD_DELTAS[period]).isoformat()
    else:
        start = earliest
        
    mint_by_day: dict[str, float] = defaultdict(float)
    burn_by_day: dict[str, float] = defaultdict(float)
    total_by_day: dict[str, float] = defaultdict(float)
    
    last24h_date = date.today() - timedelta(days=1)
    last24h_mint = 0.0
    last24h_burn = 0.0
    for r in dm_rows:
        day = r["day"]
        if date.strptime(day, "%Y-%m-%d") >= last24h_date:
            last24h_mint += r["mint_volume"]
            last24h_burn += r["burn_volume"]
            
        if not (start <= day <= end):
            continue
        mint_by_day[day] += r["mint_volume"]
        burn_by_day[day] += r["burn_volume"]
        total_by_day[day] += r["net_change"]
        
    cumulative_total:dict[str, float] = defaultdict(float)
    c = 0.0
    for day in sorted(mint_by_day):
        c += total_by_day[day]
        cumulative_total[day] = c

    points = [
        MintBurnPoint(date=day, mint=round(mint_by_day[day], 2), burn=round(burn_by_day[day], 2), total=round(total_by_day[day], 2), cumulative_total=round(cumulative_total[day], 2))
        for day in sorted(mint_by_day)
    ]
    
    
    
    

    return MintBurnResponse(
        data=points,
        total_mint=sum(mint_by_day.values()),
        total_burn=sum(burn_by_day.values()),
        total_net=sum(total_by_day.values()),
        last24h_mint=last24h_mint,
        last24h_burn=last24h_burn,
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )