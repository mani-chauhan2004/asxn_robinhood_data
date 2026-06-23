import json
from app.core.paths import DATA_DIR


def _load_rows() -> tuple[list[dict], list[str]]:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])
    tb_rows = json.loads((DATA_DIR / "token_balances.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    # Lookup maps from the enrichment sources
    balance_map = {r["token_symbol"]: r for r in tb_rows}
    price_map   = {r["symbol"]: r for r in sp_rows}
    categories  = sorted({r["category"] for r in tf_rows})

    # Deduplicate token_factory by symbol (keep first occurrence)
    seen = set()
    unique_tf = []
    for r in tf_rows:
        if r["token_symbol"] not in seen:
            seen.add(r["token_symbol"])
            unique_tf.append(r)

    total_value = sum(
        balance_map.get(r["token_symbol"], {}).get("shares_tokenized", 0.0)
        * price_map.get(r["token_symbol"], {}).get("price", 0.0)
        for r in unique_tf
    )

    rows = []
    for r in unique_tf:
        sym = r["token_symbol"]
        tb  = balance_map.get(sym, {})
        sp  = price_map.get(sym, {})

        price  = sp.get("price", 0.0)
        shares = tb.get("shares_tokenized", 0.0)
        value  = round(shares * price, 2)
        c1, c7, c30 = sp.get("change_1d"), sp.get("change_7d"), sp.get("change_30d")

        rows.append({
            "symbol":    sym,
            "name":      r["token_name"],
            "logo_url":  "",
            "category":  r["category"],
            "price":     price,
            "shares":    shares,
            "value":     value,
            "pct_total": round(value / total_value * 100, 4) if total_value else 0.0,
            "change_1d":  round(shares * c1,  2) if c1  is not None else None,
            "change_7d":  round(shares * c7,  2) if c7  is not None else None,
            "change_30d": round(shares * c30, 2) if c30 is not None else None,
        })

    return rows, categories


def get_explorer_data(
    page:       int,
    limit:      int,
    search:     str,
    category:   str | None,
    min_value:  float,
    sort_by:    str,
    sort_order: str,
) -> dict:
    rows, categories = _load_rows()

    if search:
        q = search.lower()
        rows = [r for r in rows if q in r["symbol"].lower() or q in r["name"].lower()]

    if category:
        rows = [r for r in rows if r["category"] == category]

    if min_value > 0:
        rows = [r for r in rows if r["value"] >= min_value]

    rows.sort(
        key=lambda r: (r[sort_by] if r[sort_by] is not None else 0),
        reverse=(sort_order == "desc"),
    )

    total    = len(rows)
    start    = (page - 1) * limit
    end      = start + limit
    has_next = (page + 1) if end < total else None

    return {
        "data":        rows[start:end],
        "categories":  categories,
        "nextPage": has_next,
        "totalAssets": len(rows),
    }
