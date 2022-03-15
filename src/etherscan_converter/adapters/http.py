from etherscan_converter._base.aiohttp_client import Client
from etherscan_converter.config import HttpClientConfig, config


class HttpClientException(Exception):
    """Исключение для HTTP клиента."""


class HttpClient(Client[HttpClientConfig, Exception]):
    _exception = HttpClientException





http_client = HttpClient(config.http_client)
