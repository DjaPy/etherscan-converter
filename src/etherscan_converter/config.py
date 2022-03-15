from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings

from etherscan_converter._base.aiohttp_client import ConfigClient


class HttpClientConfig(ConfigClient):

    retry_count: int = 5
    retry_timeout: float = 10

    class Config:
        env_file = '.env'


class Config(BaseSettings):
    http_client = HttpClientConfig()
    host: str = '127.0.0.1'
    port: int = 8000
    service_name: str = "etherscan_converter"

    origins: List[Optional[AnyHttpUrl]] = []  # CORS

    jaeger_enable: bool = False
    jaeger_name: str = service_name
    jaeger_host: str = 'localhost'
    jaeger_port: int = 6831

    class Config:
        env_file = '.env'


config = Config()
