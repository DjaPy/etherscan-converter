from fastapi import APIRouter

from etherscan_converter.entrypoints.api_v1.endpoints import health_check

api_router = APIRouter()
api_router.include_router(health_check.router, prefix='/health-check', tags=['Health check'])
