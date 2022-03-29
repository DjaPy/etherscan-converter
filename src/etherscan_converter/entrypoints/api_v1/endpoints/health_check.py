from fastapi import APIRouter
from starlette import status

from etherscan_converter import __version__
from etherscan_converter.entrypoints.api_v1.schemas import HealthResponseSchema

router = APIRouter()


@router.get(
    '/',
    summary='Health check',
    responses={
        status.HTTP_200_OK: {'model': HealthResponseSchema, 'description': 'Service online'},
    },
)
async def health_check() -> HealthResponseSchema:
    return HealthResponseSchema(version=__version__)
