from app.api.routes.assets import explorer as assets_explorer
from app.api.routes.assets import metrics as assets_metrics
from app.api.routes.dune import queries as dune_queries
from app.api.routes.tokenization import tvt as tokenization_tvt
from app.api.routes.tokenization import mint_burns as tokenization_mint_burns
from app.api.routes.tokenization import token_count as tokenization_token_count
from app.api.routes.tokenization import tokenized_value as tokenization_tokenized_value
from app.api.routes.tokenization import value_by_category_donut as tokenization_value_by_category_donut
from app.api.routes.tokenization import tokens_by_category_donut as tokenization_tokens_by_category_donut
from app.api.routes.tokenization import mint_burn_by_category_donut as tokenization_mint_burn_by_category_donut
from app.api.routes.tokenization import stats as tokenization_stats
from app.api.routes.mintburn import volume_usd as mintburn_volume_usd
from app.api.routes.mintburn import category_share as mintburn_category_share
from app.api.routes.mintburn import issuance_firehose as mintburn_issuance_firehose
from app.api.routes.mintburn import stats as mintburn_stats
from app.api.routes.mintburn import tokens as mintburn_tokens
from app.api.routes.mintburn import token_volume as mintburn_token_volume
from fastapi import APIRouter

router = APIRouter()
router.include_router(dune_queries.router)
router.include_router(assets_metrics.router)
router.include_router(assets_explorer.router)
router.include_router(tokenization_tvt.router)
router.include_router(tokenization_mint_burns.router)
router.include_router(tokenization_token_count.router)
router.include_router(tokenization_tokenized_value.router)
router.include_router(tokenization_value_by_category_donut.router)
router.include_router(tokenization_tokens_by_category_donut.router)
router.include_router(tokenization_mint_burn_by_category_donut.router)
router.include_router(tokenization_stats.router)
router.include_router(mintburn_volume_usd.router)
router.include_router(mintburn_category_share.router)
router.include_router(mintburn_issuance_firehose.router)
router.include_router(mintburn_stats.router)
router.include_router(mintburn_tokens.router)
router.include_router(mintburn_token_volume.router)