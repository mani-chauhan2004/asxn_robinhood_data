import json
from app.core.http_client import get_client

QUERY_IDS = {
    "daily_fee": 6872646,
    "token_factory": 6872201,
    "daily_metrics": 6872601,
    "token_balances": 6872555,
    "mint_burns": 6872222,
    "stock_prices": 6878346,
}


def _parse_response(response, empty_default=None):
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        return empty_default if empty_default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid response from API: {e}") from e


class DuneClient:
    async def _get_query_results(self, query_id: int) -> any:
        client = await get_client()
        response = await client.get(f"/query/{query_id}/results")
        data = _parse_response(response, empty_default={})
        return data.get("result", {})

    async def get_daily_fee(self) -> any:
        return await self._get_query_results(QUERY_IDS["daily_fee"])

    async def get_token_factory(self) -> any:
        return await self._get_query_results(QUERY_IDS["token_factory"])

    async def get_daily_metrics(self) -> any:
        return await self._get_query_results(QUERY_IDS["daily_metrics"])

    async def get_token_balances(self) -> any:
        return await self._get_query_results(QUERY_IDS["token_balances"])

    async def get_mint_burns(self) -> any:
        return await self._get_query_results(QUERY_IDS["mint_burns"])

    async def get_stock_prices(self) -> any:
        return await self._get_query_results(QUERY_IDS["stock_prices"])
