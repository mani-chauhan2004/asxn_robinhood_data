import json

from app.core.paths import DATA_DIR


def get_issuance_firehose(
    page: int,
    limit: int,
    search: str,
    category: str | None,
    event_type: str | None,
    token_symbol: str | None,
    sort_by: str,
    sort_order: str,
) -> dict:
    mb_rows = json.loads((DATA_DIR / "mint_burns.json").read_text()).get("rows", [])
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    addr_to_token: dict[str, dict] = {}
    for r in tf_rows:
        addr = r["contract_address"]
        if addr not in addr_to_token:
            addr_to_token[addr] = {
                "symbol": r["token_symbol"],
                "name": r["token_name"],
                "category": r["category"],
            }

    price_map = {r["symbol"]: r["price"] for r in sp_rows}
    all_categories: set[str] = set()

    rows: list[dict] = []
    for r in mb_rows:
        token = addr_to_token.get(r["contract_address"])
        if not token:
            continue
        sym = token["symbol"]
        price = price_map.get(sym, 0.0)
        all_categories.add(token["category"])
        rows.append({
            "timestamp": r["block_time"],
            "token_name": token["name"],
            "symbol": sym,
            "type": r["type"].upper(),
            "amount": r["amount"],
            "value_usd": round(r["amount"] * price, 2),
            "category": token["category"],
            "tx_hash": r["tx_hash"],
        })

    if search:
        q = search.lower()
        rows = [r for r in rows if q in r["symbol"].lower() or q in r["token_name"].lower()]

    if category:
        rows = [r for r in rows if r["category"] == category]

    if event_type:
        rows = [r for r in rows if r["type"] == event_type]

    if token_symbol:
        rows = [r for r in rows if r["symbol"] == token_symbol]

    rows.sort(
        key=lambda r: (r[sort_by] if r[sort_by] is not None else ""),
        reverse=(sort_order == "desc"),
    )

    total = len(rows)
    start = (page - 1) * limit
    end = start + limit
    has_next = (page + 1) if end < total else None

    return {
        "data": rows[start:end],
        "categories": sorted(all_categories),
        "nextPage": has_next,
        "totalEvents": total,
    }
