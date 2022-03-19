from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings

from etherscan_converter._base.aiohttp_client import ConfigClient


class EtherscanConfig(ConfigClient):

    retry_count: int = 5
    retry_timeout: float = 10
    apikey: str

    class Config:
        env_prefix = 'ETH_'
        env_file = '.env'


class Config(BaseSettings):
    eth_client = EtherscanConfig()
    host: str = '127.0.0.1'
    port: int = 8000
    service_name: str = "etherscan_converter"

    origins: List[Optional[AnyHttpUrl]] = []  # CORS

    class Config:
        env_file = '.env'


config = Config()
