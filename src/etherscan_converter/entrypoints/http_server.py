from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from etherscan_converter.adapters.etherscan_client import etherscan_client
from etherscan_converter.config import Config, config
from etherscan_converter.entrypoints.api_v1.api import api_router_v1


async def startup_client() -> None:
    await etherscan_client.start()


async def shutdown_client() -> None:
    await etherscan_client.stop()


def get_application(app_config: Config) -> FastAPI:

    app = FastAPI(
        title='Etherscan converter',
        description='Service for converting data from Etherscan',
        docs_url='/doc',
        on_startup=[startup_client],
        on_shutdown=[shutdown_client],
    )

    app.state.config = app_config

    allow_origins = [str(origin) for origin in app_config.origins]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(api_router_v1)

    return app


app_server = get_application(config)
