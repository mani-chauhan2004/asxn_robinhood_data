import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# Data cache directory (gitignored, populated by scripts/cache_dune_queries.py)
DATA_DIR = PROJECT_ROOT / "data"

# Reference files used by scripts
SYMBOLS_FILE     = PROJECT_ROOT / "lib" / "token_symbols_array.json"
TOKEN_FACTORY    = DATA_DIR / "token_factory.json"
STOCK_PRICES_CSV  = DATA_DIR / "robinhood_stock_prices.csv"
ASSETS_METRICS    = DATA_DIR / "assets" / "assets_metrics.json"

# Logging
LOG_CONFIG_FILE = PROJECT_ROOT / "app" / "logging" / "config" / "config.json"

# All writable output paths — call ensure_dirs() before any script writes files
_OUTPUT_FILES = [STOCK_PRICES_CSV, ASSETS_METRICS]

def ensure_dirs() -> None:
    for path in _OUTPUT_FILES:
        path.parent.mkdir(parents=True, exist_ok=True)
