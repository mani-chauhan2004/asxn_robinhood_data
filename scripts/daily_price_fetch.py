import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
load_dotenv(_PROJECT_ROOT / ".env")

from app.core.paths import STOCK_PRICES_CSV, SYMBOLS_FILE  # noqa: E402

DUNE_API_KEY  = os.getenv("ROBINHOOD_DATA_DUNE_API_KEY")
DUNE_USERNAME = os.getenv("ROBINHOOD_DATA_DUNE_USERNAME")
TABLE_NAME    = "robinhood_stock_prices"

if not DUNE_API_KEY or not DUNE_USERNAME:
    print("ERROR: ROBINHOOD_DATA_DUNE_API_KEY or ROBINHOOD_DATA_DUNE_USERNAME not set in .env", file=sys.stderr)
    sys.exit(1)

# ── Load symbols ───────────────────────────────────────────────────────────────
with SYMBOLS_FILE.open("r", encoding="utf-8") as f:
    symbols = json.load(f)

# ── Step 1: Fetch price data from yfinance ────────────────────────────────────
rows = []

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info
        hist   = ticker.history(period="35d")

        if hist.empty:
            print(f"  [SKIP] {symbol}: no data")
            continue

        price_today   = hist["Close"].iloc[-1]

        price_1d_ago  = hist["Close"].iloc[-2]  if len(hist) >= 2  else None
        change_1d     = round(price_today - price_1d_ago, 4) if price_1d_ago else None

        price_7d_ago  = hist["Close"].iloc[-8]  if len(hist) >= 8  else hist["Close"].iloc[0]
        change_7d     = round(price_today - price_7d_ago, 4)

        price_30d_ago = hist["Close"].iloc[-31] if len(hist) >= 31 else hist["Close"].iloc[0]
        change_30d    = round(price_today - price_30d_ago, 4)

        asset_name    = info.get("longName") or info.get("shortName") or symbol
        category      = info.get("quoteType", "Unknown")

        rows.append({
            "symbol":     symbol,
            "asset_name": asset_name,
            "category":   category,
            "price":      round(price_today, 4),
            "change_1d":  change_1d,
            "change_7d":  change_7d,
            "change_30d": change_30d,
            "as_of_date": hist.index[-1].strftime("%Y-%m-%d"),
        })

        print(f"  [OK] {symbol}: ${round(price_today, 2)} | 1D: {change_1d} | 7D: {change_7d} | 30D: {change_30d}")

    except Exception as e:
        print(f"  [FAIL] {symbol}: {e}")

df = pd.DataFrame(rows)
print(f"\nFetched {len(df)}/{len(symbols)} symbols")

# ── Step 2: Save local CSV ────────────────────────────────────────────────────
STOCK_PRICES_CSV.parent.mkdir(exist_ok=True)
df.to_csv(STOCK_PRICES_CSV, index=False)
print(f"Saved → {STOCK_PRICES_CSV}")

# ── Step 3: Upload to Dune ────────────────────────────────────────────────────
print("\nUploading to Dune...")

payload = {
    "table_name":  TABLE_NAME,
    "description": "Robinhood tokenized stock prices from yfinance — 1D/7D/30D change",
    "data":        df.to_csv(index=False),
    "is_private":  False,
}

response = requests.post(
    "https://api.dune.com/api/v1/table/upload/csv",
    headers={"X-Dune-Api-Key": DUNE_API_KEY},
    data=json.dumps(payload),
)

if response.status_code == 200:
    print("  [OK] Upload successful!")
    print(f"       Query in Dune: SELECT * FROM dune.{DUNE_USERNAME}.dataset_{TABLE_NAME}")
else:
    print(f"  [FAIL] Upload failed: {response.status_code} — {response.text}", file=sys.stderr)
    sys.exit(1)
