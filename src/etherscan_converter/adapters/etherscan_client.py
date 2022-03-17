from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field
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
    blockHash: str
    blockNumber: str
    _from: str = Field(alias='from')
    gas: str
    gasPrice: str
    maxFeePerGas: str
    maxPriorityFeePerGas: str
    _hash: str = Field(alias='hash')
    input: str
    nonce: str
    to: str
    transactionIndex: str
    value: str
    type: str
    accssList: List[str]
    chainId: str
    v: str
    r: str
    s: str


class HttpClient(Client[EtherscanConfig, Exception]):
    _exception = HttpClientException
    cfg: EtherscanConfig

    async def get_trx_by_hash(self, trx_hash: str) -> TrxByHashResponse:
        result = await self._send_request(
            paht=f'/api?module=proxy&action=eth_getTransactionByHash&txhash={trx_hash}&apikey={self.cfg.apikey}',
            response_schema=ResultResponse[TrxByHashResponse],
            error_schema=None,
        )
        if result.result:
            return result.result


etherscan_client = HttpClient(config.http_client)
