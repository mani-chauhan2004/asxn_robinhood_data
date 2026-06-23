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