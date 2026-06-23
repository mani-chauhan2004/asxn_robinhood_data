import json
from collections import defaultdict
from datetime import date, timedelta
from warnings import warn

from app.core.paths import DATA_DIR
from app.schemas.tokenization import (
    AssetsTokenizedOverTimePoint,
    AssetsTokenizedOverTimeResponse,
    MintBurnByCategoryDonutResponse,
    MintBurnByCategoryDonutSlice,
    MintBurnPoint,
    MintBurnResponse,
    TimePeriod,
    TokensByCategoryDonutResponse,
    TokensByCategoryDonutSlice,
    TVTPoint,
    TVTResponse,
    ValueByCategoryDonutResponse,
    ValueByCategoryDonutSlice,
    ValueByCategoryPoint,
    ValueByCategoryResponse,
)

_PERIOD_DELTAS = {
    TimePeriod.one_day: timedelta(days=1),
    TimePeriod.seven_days: timedelta(days=7),
    TimePeriod.one_month: timedelta(days=30),
    TimePeriod.three_months: timedelta(days=90),
    TimePeriod.one_year: timedelta(days=365),
}


def get_tvt(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> TVTResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    all_days = sorted({r["day"] for r in dm_rows})
    earliest = all_days[0] if all_days else date.today().isoformat()
    latest = all_days[-1] if all_days else date.today().isoformat()

    end = to_date.isoformat() if to_date else latest
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
    latest = all_days[-1] if all_days else date.today().isoformat()

    end = to_date.isoformat() if to_date else latest
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
    last_30d_date = date.today() - timedelta(days=30)
    last24h_mint = 0.0
    last24h_burn = 0.0
    last24h_net = 0.0
    last_30d_mint = 0.0
    last_30d_burn = 0.0
    last_30d_net = 0.0
    for r in dm_rows:
        day = r["day"]
        if date.strptime(day, "%Y-%m-%d") >= last24h_date:
            last24h_mint += r["mint_volume"]
            last24h_burn += r["burn_volume"]
            last24h_net += r["net_change"]
        if date.strptime(day, "%Y-%m-%d") >= last_30d_date:
            last_30d_mint += r["mint_volume"]
            last_30d_burn += r["burn_volume"]
            last_30d_net += r["net_change"]
            
        if not (start <= day <= end):
            continue
        mint_by_day[day] += r["mint_volume"]
        burn_by_day[day] += r["burn_volume"]
        total_by_day[day] += r["net_change"]

    cumulative_total: dict[str, float] = defaultdict(float)
    c = 0.0
    for day in sorted(mint_by_day):
        c += total_by_day[day]
        cumulative_total[day] = c

    points = [
        MintBurnPoint(
            date=day,
            mint=round(mint_by_day[day], 2),
            burn=round(burn_by_day[day], 2),
            total=round(total_by_day[day], 2),
            cumulative_total=round(cumulative_total[day], 2),
        )
        for day in sorted(mint_by_day)
    ]

    return MintBurnResponse(
        data=points,
        total_mint=sum(mint_by_day.values()),
        total_burn=sum(burn_by_day.values()),
        total_net=sum(total_by_day.values()),
        last24h_mint=last24h_mint,
        last24h_burn=last24h_burn,
        last24h_net=last24h_net,
        last_30d_mint=last_30d_mint,
        last_30d_burn=last_30d_burn,
        last_30d_net=last_30d_net,
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )


def get_assets_tokenized_over_time(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> AssetsTokenizedOverTimeResponse:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])
    
    def block_time_to_date(block_time: str) -> str:
        return date.strptime(block_time.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S.%f').isoformat()

    all_days = sorted({block_time_to_date(r["block_time"]) for r in tf_rows})
    earliest = all_days[0] if all_days else date.today().isoformat()
    latest = all_days[-1] if all_days else date.today().isoformat()

    end = to_date.isoformat() if to_date else latest
    if from_date:
        start = from_date.isoformat()
    elif period and period != TimePeriod.all:
        start = (date.fromisoformat(end) - _PERIOD_DELTAS[period]).isoformat()
    else:
        start = earliest
        
    class CountByDay:
        def __init__(self):
            self.count = 0
            self.symbols = []
        
    count_by_day: dict[str, CountByDay] = defaultdict(CountByDay)
    for r in tf_rows:
        day = block_time_to_date(r["block_time"])
        if not (start <= day <= end):
            continue
        count_by_day[day].symbols.append(r["token_symbol"])

    cumulative_count: dict[str, float] = defaultdict(float)
    c = 0.0
    for day in sorted(count_by_day):
        count_by_day[day].count = len(set(count_by_day[day].symbols))
        count_by_day[day].symbols = list(set(count_by_day[day].symbols))
        c += count_by_day[day].count
        cumulative_count[day] = c
        
    points = [
        AssetsTokenizedOverTimePoint(
            date=day,
            count=count_by_day[day].count,
            cumulative_count=cumulative_count[day],
            current_day_tokenized=count_by_day[day].symbols,
        )
        for day in sorted(count_by_day)
    ]
    
    return AssetsTokenizedOverTimeResponse(
        data=points,
        current_count=points[-1].count if points else 0.0,
        total_count=cumulative_count[latest],
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )
    
    
def get_value_by_category(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> ValueByCategoryResponse:
    
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])
    
    price_map = {r["symbol"]: r["price"] for r in sp_rows}
    
    all_days = sorted({r["day"] for r in dm_rows})
    earliest = all_days[0] if all_days else date.today().isoformat()
    latest = all_days[-1] if all_days else date.today().isoformat()
    
    end = to_date.isoformat() if to_date else latest
    if from_date:
        start = from_date.isoformat()
    elif period and period != TimePeriod.all:
        start = (date.fromisoformat(end) - _PERIOD_DELTAS[period]).isoformat()
    else:
        start = earliest
        
    value_by_category: dict[str, dict[str,float]] = defaultdict(dict)
    for r in dm_rows:
        day = r["day"]
        if not (start <= day <= end):
            continue
        
        if r["token_symbol"] not in price_map:
            warn(f"Token symbol {r['token_symbol']} not found in price map")
        value_by_category[day][r["category"]] = value_by_category[day].get(r["category"], 0.0) + r["cumulative_tvl"] * price_map.get(r["token_symbol"], 0.0)
        
    pct_by_category: dict[str, dict[str,float]] = defaultdict(dict)
    for day in sorted(value_by_category):
        total = sum(value_by_category[day].values())
        for category in value_by_category[day]:
            pct_by_category[day][category] = value_by_category[day][category] / total
        
    points = [
        ValueByCategoryPoint(
            date=day,
            categories=value_by_category[day],
            pct_by_category=pct_by_category[day],
        )
        for day in sorted(value_by_category)
    ]
    
    return ValueByCategoryResponse(
        data=points,
        period=period,
        earliest_date=earliest,
        latest_date=latest,
        categories = sorted(set(category for day in sorted(value_by_category) for category in value_by_category[day]))
    )


def get_value_by_category_donut() -> ValueByCategoryDonutResponse:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])
    tb_rows = json.loads((DATA_DIR / "token_balances.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    balance_map = {r["token_symbol"]: r for r in tb_rows}
    price_map = {r["symbol"]: r for r in sp_rows}

    seen: set[str] = set()
    agg: dict[str, float] = defaultdict(float)
    for r in tf_rows:
        sym = r["token_symbol"]
        if sym in seen:
            continue
        seen.add(sym)
        shares = balance_map.get(sym, {}).get("shares_tokenized", 0.0)
        price = price_map.get(sym, {}).get("price", 0.0)
        agg[r["category"]] += shares * price

    categories = sorted(agg.keys())
    slices = [
        ValueByCategoryDonutSlice(category=cat, current_value_usd=round(agg[cat], 2))
        for cat in categories
    ]
    total = round(sum(s.current_value_usd for s in slices), 2)

    return ValueByCategoryDonutResponse(
        slices=slices,
        total_value_usd=total,
        categories=categories,
    )


def get_tokens_by_category_donut() -> TokensByCategoryDonutResponse:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])

    seen: dict[str, str] = {}
    for r in tf_rows:
        if r["token_symbol"] not in seen:
            seen[r["token_symbol"]] = r["category"]

    count_by_cat: dict[str, int] = defaultdict(int)
    for cat in seen.values():
        count_by_cat[cat] += 1

    categories = sorted(count_by_cat.keys())
    slices = [
        TokensByCategoryDonutSlice(category=cat, token_count=count_by_cat[cat])
        for cat in categories
    ]

    return TokensByCategoryDonutResponse(
        slices=slices,
        total_token_count=sum(s.token_count for s in slices),
        categories=categories,
    )


def get_mint_burn_by_category_donut() -> MintBurnByCategoryDonutResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])

    if not dm_rows:
        return MintBurnByCategoryDonutResponse(
            slices=[], total_mint_24h=0, total_burn_24h=0, total_net_24h=0, categories=[]
        )

    latest_day = max(r["day"] for r in dm_rows)

    mint_by_cat: dict[str, float] = defaultdict(float)
    burn_by_cat: dict[str, float] = defaultdict(float)
    for r in dm_rows:
        if r["day"] == latest_day:
            mint_by_cat[r["category"]] += r["mint_volume"]
            burn_by_cat[r["category"]] += r["burn_volume"]

    categories = sorted(set(mint_by_cat.keys()) | set(burn_by_cat.keys()))
    slices = [
        MintBurnByCategoryDonutSlice(
            category=cat,
            mint_24h=round(mint_by_cat[cat], 2),
            burn_24h=round(burn_by_cat[cat], 2),
            net_24h=round(mint_by_cat[cat] - burn_by_cat[cat], 2),
        )
        for cat in categories
    ]

    return MintBurnByCategoryDonutResponse(
        slices=slices,
        total_mint_24h=round(sum(s.mint_24h for s in slices), 2),
        total_burn_24h=round(sum(s.burn_24h for s in slices), 2),
        total_net_24h=round(sum(s.net_24h for s in slices), 2),
        categories=categories,
    )