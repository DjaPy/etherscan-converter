"""Конфигурация для тестирования."""
import asyncio
from functools import partial
from typing import List, Optional

import pytest
import uvicorn
from aiohttp import request
from aioresponses import aioresponses
from entrypoints.http_server import get_application
from faker import Faker
from fastapi import FastAPI

from etherscan_converter.config import Config

pytest_plugins = ['fixtures_generate_data']


class UvicornTestServer(uvicorn.Server):
    """Uvicorn test server.

    https://github.com/miguelgrinberg/python-socketio/issues/332#issuecomment-712928157
    """

    def __init__(self, app: FastAPI, host: str, port: int):
        """Create a Uvicorn test server

        Args:
            app (FastAPI, optional): the FastAPI app. Defaults to main.app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to PORT.
        """
        self._startup_done = asyncio.Event()
        super().__init__(config=uvicorn.Config(app, host=host, port=port))

    async def startup(self, sockets: Optional[List] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        await self._serve_task


@pytest.fixture
def fake():
    return Faker('ru-RU')


@pytest.fixture(scope='session')
def config():
    config = Config()
    return config


@pytest.fixture
def app(config):
    app = get_application(config)
    return app


@pytest.fixture
async def server(config, aiohttp_unused_port, app):
    """Start server as test fixture and tear down after test"""
    config.port = aiohttp_unused_port()
    server_uvicorn = UvicornTestServer(app, config.host, config.port)
    await server_uvicorn.up()
    yield server
    await server_uvicorn.down()


@pytest.fixture
async def client(config):
    class _Client:
        def __getattribute__(self, item):
            return partial(request, method=item)

    return _Client()


@pytest.fixture
def mock_responses(config):
    """Mocking all requests ethterscan"""
    with aioresponses() as m:
        yield m
