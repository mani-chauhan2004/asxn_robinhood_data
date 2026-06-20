"""
Fetch all Dune query results and save them as JSON to the data/ directory.

Usage:
    python scripts/cache_dune_queries.py            # use Dune's cached results
    python scripts/cache_dune_queries.py --fresh    # trigger fresh execution first

Cron example (every 5 minutes, cached):
    */5 * * * * cd /path/to/robinhood && venv/bin/python scripts/cache_dune_queries.py

Cron example (daily fresh run at 1am):
    0 1 * * * cd /path/to/robinhood && venv/bin/python scripts/cache_dune_queries.py --fresh
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Allow importing from app/ when run as a standalone script
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
load_dotenv(_PROJECT_ROOT / ".env")

from app.core.paths import ASSETS_METRICS, DATA_DIR, ensure_dirs  # noqa: E402

API_KEY = os.getenv("ROBINHOOD_DATA_DUNE_API_KEY")
BASE_URL = os.getenv("ROBINHOOD_DATA_DUNE_API_BASE_URL", "https://api.dune.com/api/v1").rstrip("/")

QUERIES = {
    "daily_fee":      6872646,
    "token_factory":  6872201,
    "daily_metrics":  6872601,
    "token_balances": 6872555,
    "mint_burns":     6872222,
    "stock_prices":   6878346,
}

POLL_INTERVAL = 3   # seconds between status checks
POLL_TIMEOUT  = 120 # seconds before giving up on a fresh execution


def headers() -> dict:
    return {"X-Dune-Api-Key": API_KEY}


def fetch_cached(query_id: int) -> dict:
    url = f"{BASE_URL}/query/{query_id}/results"
    r = requests.get(url, headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json().get("result", {})


def execute_fresh(query_id: int) -> dict:
    # Trigger execution
    r = requests.post(f"{BASE_URL}/query/{query_id}/execute", headers=headers(), timeout=30)
    r.raise_for_status()
    execution_id = r.json()["execution_id"]

    # Poll until complete
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        status_r = requests.get(
            f"{BASE_URL}/execution/{execution_id}/status",
            headers=headers(),
            timeout=30,
        )
        status_r.raise_for_status()
        state = status_r.json().get("state", "")

        if state == "QUERY_STATE_COMPLETED":
            break
        if state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED", "QUERY_STATE_EXPIRED"):
            raise RuntimeError(f"Execution {execution_id} ended with state: {state}")

        time.sleep(POLL_INTERVAL)
    else:
        raise TimeoutError(f"Execution {execution_id} did not complete within {POLL_TIMEOUT}s")

    # Fetch results
    results_r = requests.get(
        f"{BASE_URL}/execution/{execution_id}/results",
        headers=headers(),
        timeout=30,
    )
    results_r.raise_for_status()
    return results_r.json().get("result", {})


def compute_assets_metrics() -> None:
    tf_rows = json.loads((DATA_DIR / "token_factory.json").read_text()).get("rows", [])
    tb_rows = json.loads((DATA_DIR / "token_balances.json").read_text()).get("rows", [])
    sp_rows = json.loads((DATA_DIR / "stock_prices.json").read_text()).get("rows", [])

    price_map = {r["symbol"]: r["price"] for r in sp_rows}

    total_assets = len({r["token_symbol"] for r in tf_rows})
    categories   = len({r["category"] for r in tf_rows})

    total_value  = 0.0
    largest_symbol, largest_name, largest_value = None, None, 0.0

    for r in tb_rows:
        sym   = r["token_symbol"]
        value = r["shares_tokenized"] * price_map.get(sym, 0.0)
        total_value += value
        if value > largest_value:
            largest_value  = value
            largest_symbol = sym
            largest_name   = r["token_name"]

    metrics = {
        "total_assets":          total_assets,
        "total_value_tokenized": round(total_value, 2),
        "largest_asset": {
            "symbol": largest_symbol,
            "name":   largest_name,
            "value":  round(largest_value, 2),
        },
        "categories": categories,
    }

    ASSETS_METRICS.write_text(json.dumps(metrics, indent=2))
    print(f"  [OK] assets_metrics → {ASSETS_METRICS.name}")


def save(name: str, data: dict) -> Path:
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def main(fresh: bool) -> None:
    if not API_KEY:
        print("ERROR: ROBINHOOD_DATA_DUNE_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    ensure_dirs()
    mode = "fresh execution" if fresh else "cached results"
    print(f"Fetching {len(QUERIES)} queries ({mode})...\n")

    ok = 0
    for name, query_id in QUERIES.items():
        try:
            if fresh:
                data = execute_fresh(query_id)
            else:
                data = fetch_cached(query_id)

            path = save(name, data)
            rows = len(data.get("rows", []))
            print(f"  [OK] {name} → {path.name}  ({rows} rows)")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] {name} (query {query_id}): {e}", file=sys.stderr)

    print(f"\nDone: {ok}/{len(QUERIES)} queries saved to {DATA_DIR}/")
    if ok < len(QUERIES):
        sys.exit(1)

    print("\nComputing derived metrics...")
    try:
        compute_assets_metrics()
    except Exception as e:
        print(f"  [FAIL] assets_metrics: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cache Dune query results locally.")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Trigger a fresh query execution on Dune before fetching results.",
    )
    args = parser.parse_args()
    main(fresh=args.fresh)
