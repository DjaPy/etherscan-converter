from fastapi import APIRouter

from entrypoints.api_v1.endpoints import transaction_data
from etherscan_converter.entrypoints.api_v1.endpoints import health_check

api_router_v1 = APIRouter(prefix='/v1')
api_router_v1.include_router(health_check.router, prefix='/health-check', tags=['Health check'])
api_router_v1.include_router(transaction_data.router, prefix='/trx_data', tags=['Transaction data'])
