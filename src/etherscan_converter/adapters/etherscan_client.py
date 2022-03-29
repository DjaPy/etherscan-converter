from typing import Generic, List, TypeVar, Optional, Any

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from etherscan_converter._base.aiohttp_client import Client
from etherscan_converter.config import EtherscanConfig, config

ParamType = TypeVar('ParamType')


class HttpClientException(Exception):
    """Исключение для HTTP клиента."""


class ResultResponseProxy(GenericModel, Generic[ParamType]):
    jsonrpc: str
    id: int
    result: ParamType


class ResultResponseContract(GenericModel, Generic[ParamType]):
    status: str
    message: str
    result: ParamType


ABI = str


class SourceCodeContract(BaseModel):
    ABI: str
    ContractName: str
    CompilerVersion: str
    OptimizationUsed: str
    Runs: str
    ConstructorArguments: str
    EVMVersion: str
    Library: str
    LicenseType: str
    Proxy: str
    Implementation: str
    SwarmSource: str


SourceCodeContracts = List[SourceCodeContract]


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
    accssList: Optional[List[str]]
    chainId: str
    v: str
    r: str
    s: str

    class Config:
        by_alias = False


class ResponseErrorSchema(BaseModel):
    status: str
    message: str
    result: str


class EthClient(Client[EtherscanConfig, Exception]):
    _exception = HttpClientException
    cfg: EtherscanConfig

    async def get_trx_by_hash(self, trx_hash: str) -> Optional[ResultResponseProxy]:
        url = self.url / 'api' % {
            'module': 'proxy', 'action': 'eth_getTransactionByHash', 'txhash': trx_hash, 'apikey': self.cfg.apikey
        }
        return await self._send_request(
            path=url,
            response_schema=ResultResponseProxy[TrxByHashResponse],
            error_schema=ResponseErrorSchema,
        )

    async def get_abi(self, address: str) -> Optional[ResultResponseContract]:
        url = self.url / 'api' % {
            'module': 'contract', 'action': 'getabi', 'address': address, 'apikey': self.cfg.apikey
        }
        return await self._send_request(
            path=url,
            response_schema=ResultResponseContract[ABI],
            error_schema=ResponseErrorSchema,
        )

    async def get_source_code_contract(self, address: str):
        url = self.url / 'api' % {
            'module': 'contract', 'action': 'getsourcecode', 'address': address, 'apikey': self.cfg.apikey
        }
        return await self._send_request(
            path=url,
            response_schema=ResultResponseContract[SourceCodeContracts],
            error_schema=ResponseErrorSchema,
        )


etherscan_client = EthClient(config.eth)
