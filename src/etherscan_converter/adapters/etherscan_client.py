from typing import TypeVar, Generic

from pydantic import BaseModel
from pydantic.generics import GenericModel

from etherscan_converter._base.aiohttp_client import Client
from etherscan_converter.config import EtherscanConfig, config

ParamType = TypeVar('ParamType')


class HttpClientException(Exception):
    """Исключение для HTTP клиента."""


class ResultResponse(GenericModel, Generic[ParamType]):
    json_rpc: str
    id: int
    result: ParamType


class TrxByHashResponse(BaseModel):
    ...


class HttpClient(Client[EtherscanConfig, Exception]):
    _exception = HttpClientException
    cfg: EtherscanConfig

    async def get_trx_by_hash(self, trx_hash:str) -> TrxByHashResponse:
        result = await self._send_request(
            paht=f'/api?module=proxy&action=eth_getTransactionByHash&txhash={trx_hash}&apikey={self.cfg.apikey}',
            response_schema=ResultResponse[TrxByHashResponse],
        )
        if result.result:
            return result.result




http_client = HttpClient(config.http_client)
