from fastapi import APIRouter, HTTPException
from app.services.dune_client import DuneClient
from app.services.cache import cache

router = APIRouter(
    prefix="/dune",
    tags=["dune"],
)

dune = DuneClient()

CACHE_TTL = 300  # 5 minutes


@router.get("/daily-fee")
async def get_daily_fee():
    """
    Get Robinhood daily fee data from Dune Analytics.

    Returns on-chain daily fee metrics. Cached for 5 minutes.
    """
    cache_key = "dune:daily_fee"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_daily_fee()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/token-factory")
async def get_token_factory():
    """
    Get Robinhood token factory data from Dune Analytics.

    Returns on-chain token factory metrics. Cached for 5 minutes.
    """
    cache_key = "dune:token_factory"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_token_factory()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/daily-metrics")
async def get_daily_metrics():
    """
    Get Robinhood daily metrics from Dune Analytics.

    Returns on-chain daily metrics. Cached for 5 minutes.
    """
    cache_key = "dune:daily_metrics"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_daily_metrics()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/token-balances")
async def get_token_balances():
    """
    Get Robinhood token balances from Dune Analytics.

    Returns on-chain token balance data. Cached for 5 minutes.
    """
    cache_key = "dune:token_balances"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_token_balances()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/mint-burns")
async def get_mint_burns():
    """
    Get Robinhood mint/burn data from Dune Analytics.

    Returns on-chain mint and burn metrics. Cached for 5 minutes.
    """
    cache_key = "dune:mint_burns"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_mint_burns()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/stock-prices")
async def get_stock_prices():
    """
    Get Robinhood stock prices from Dune Analytics.

    Returns on-chain stock price data. Cached for 5 minutes.
    """
    cache_key = "dune:stock_prices"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await dune.get_stock_prices()
        await cache.set_cache(cache_key, data, CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))