import json
from collections import defaultdict
from datetime import date, timedelta

from app.core.paths import DATA_DIR
from app.schemas.mintburn import (
    MintBurnCategorySharePoint,
    MintBurnCategoryShareResponse,
    MintBurnStatsResponse,
    MintBurnToken,
    MintBurnTokensResponse,
    MintBurnVolumeUsdPoint,
    MintBurnVolumeUsdResponse,
    TokenMintBurn,
    TokenVolumePoint,
    TokenVolumeResponse,
)
from app.schemas.tokenization import TimePeriod

_PERIOD_DELTAS = {
    TimePeriod.one_day: timedelta(days=1),
    TimePeriod.seven_days: timedelta(days=7),
    TimePeriod.one_month: timedelta(days=30),
    TimePeriod.three_months: timedelta(days=90),
    TimePeriod.one_year: timedelta(days=365),
}


def get_mintburn_stats() -> MintBurnStatsResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    days = sorted({r["day"] for r in dm_rows})
    today = days[-1] if days else date.today().isoformat()
    yesterday = days[-2] if len(days) >= 2 else today

    cum_mint = 0.0
    cum_burn = 0.0
    mint_today = 0.0
    mint_yesterday = 0.0

    for r in dm_rows:
        price = price_map.get(r["token_symbol"], 0.0)
        cum_mint += r["mint_volume"] * price
        cum_burn += r["burn_volume"] * price
        if r["day"] == today:
            mint_today += r["mint_volume"] * price
        if r["day"] == yesterday:
            mint_yesterday += r["mint_volume"] * price

    mint_change_pct = round((mint_today - mint_yesterday) / mint_yesterday * 100, 1) if mint_yesterday else 0.0

    return MintBurnStatsResponse(
        cumulative_mint_usd=round(cum_mint, 2),
        cumulative_burn_usd=round(cum_burn, 2),
        cumulative_net_usd=round(cum_mint - cum_burn, 2),
        mint_24h_usd=round(mint_today, 2),
        mint_24h_change_pct=mint_change_pct,
    )


def get_mint_burn_volume_usd(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
    token_symbol: str | None = None,
) -> MintBurnVolumeUsdResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    if token_symbol:
        dm_rows = [r for r in dm_rows if r["token_symbol"] == token_symbol]

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

    tokens_by_day: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: {"mint": 0.0, "burn": 0.0})
    )

    for r in dm_rows:
        day = r["day"]
        if not (start <= day <= end):
            continue
        sym = r["token_symbol"]
        price = price_map.get(sym, 0.0)
        tokens_by_day[day][sym]["mint"] += r["mint_volume"] * price
        tokens_by_day[day][sym]["burn"] += r["burn_volume"] * price

    cum_mint = 0.0
    cum_burn = 0.0
    points: list[MintBurnVolumeUsdPoint] = []
    for day in sorted(tokens_by_day):
        day_tokens: dict[str, TokenMintBurn] = {}
        day_mint = 0.0
        day_burn = 0.0
        for sym, vals in sorted(tokens_by_day[day].items()):
            m = round(vals["mint"], 2)
            b = round(vals["burn"], 2)
            if m > 0 or b > 0:
                day_tokens[sym] = TokenMintBurn(mint_usd=m, burn_usd=b)
            day_mint += vals["mint"]
            day_burn += vals["burn"]

        cum_mint += day_mint
        cum_burn += day_burn
        points.append(MintBurnVolumeUsdPoint(
            date=day,
            tokens=day_tokens,
            total_mint_usd=round(day_mint, 2),
            total_burn_usd=round(day_burn, 2),
            cumulative_mint_usd=round(cum_mint, 2),
            cumulative_burn_usd=round(cum_burn, 2),
            cumulative_net_usd=round(cum_mint - cum_burn, 2),
        ))

    return MintBurnVolumeUsdResponse(
        data=points,
        total_mint_usd=round(cum_mint, 2),
        total_burn_usd=round(cum_burn, 2),
        total_net_usd=round(cum_mint - cum_burn, 2),
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )


def get_mintburn_tokens() -> MintBurnTokensResponse:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])

    seen: set[str] = set()
    tokens: list[MintBurnToken] = []
    for r in tf_rows:
        sym = r["token_symbol"]
        if sym not in seen:
            seen.add(sym)
            tokens.append(MintBurnToken(
                symbol=sym,
                name=r["token_name"],
                category=r["category"],
            ))

    tokens.sort(key=lambda t: t.symbol)
    return MintBurnTokensResponse(tokens=tokens, total=len(tokens))


def get_token_volume(
    token_symbol: str | None,
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> TokenVolumeResponse:
    dm_rows = json.loads((DATA_DIR / "daily_metrics.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    if token_symbol:
        dm_rows = [r for r in dm_rows if r["token_symbol"] == token_symbol]

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

    for r in dm_rows:
        day = r["day"]
        if not (start <= day <= end):
            continue
        p = price_map.get(r["token_symbol"], 0.0)
        mint_by_day[day] += r["mint_volume"] * p
        burn_by_day[day] += r["burn_volume"] * p

    cum_mint = 0.0
    cum_burn = 0.0
    points: list[TokenVolumePoint] = []
    for day in sorted(mint_by_day):
        m = mint_by_day[day]
        b = burn_by_day[day]
        cum_mint += m
        cum_burn += b
        points.append(TokenVolumePoint(
            date=day,
            mint_usd=round(m, 2),
            burn_usd=round(b, 2),
            net_usd=round(m - b, 2),
            cumulative_mint_usd=round(cum_mint, 2),
            cumulative_burn_usd=round(cum_burn, 2),
            cumulative_net_usd=round(cum_mint - cum_burn, 2),
        ))

    return TokenVolumeResponse(
        token_symbol=token_symbol or "ALL_ASSETS",
        data=points,
        total_mint_usd=round(cum_mint, 2),
        total_burn_usd=round(cum_burn, 2),
        total_net_usd=round(cum_mint - cum_burn, 2),
        period=period,
        earliest_date=earliest,
        latest_date=latest,
    )


def get_mint_burn_category_share(
    period: TimePeriod | None,
    from_date: date | None,
    to_date: date | None,
) -> MintBurnCategoryShareResponse:
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

    mint_by_day_cat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    burn_by_day_cat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    all_categories: set[str] = set()

    for r in dm_rows:
        day = r["day"]
        if not (start <= day <= end):
            continue
        price = price_map.get(r["token_symbol"], 0.0)
        cat = r["category"]
        all_categories.add(cat)
        mint_by_day_cat[day][cat] += r["mint_volume"] * price
        burn_by_day_cat[day][cat] += r["burn_volume"] * price

    categories = sorted(all_categories)
    points: list[MintBurnCategorySharePoint] = []
    for day in sorted(mint_by_day_cat):
        total_mint = sum(mint_by_day_cat[day].values())
        total_burn = sum(burn_by_day_cat[day].values())

        mint_pct: dict[str, float] = {}
        burn_pct: dict[str, float] = {}
        for cat in categories:
            mint_pct[cat] = round(mint_by_day_cat[day][cat] / total_mint * 100, 2) if total_mint > 0 else 0.0
            burn_pct[cat] = round(burn_by_day_cat[day][cat] / total_burn * 100, 2) if total_burn > 0 else 0.0

        points.append(MintBurnCategorySharePoint(
            date=day,
            mint_share_pct=mint_pct,
            burn_share_pct=burn_pct,
        ))

    return MintBurnCategoryShareResponse(
        data=points,
        period=period,
        earliest_date=earliest,
        latest_date=latest,
        categories=categories,
    )
