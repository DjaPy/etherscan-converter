import pytest
from starlette import status
from yarl import URL

from etherscan_converter.adapters.etherscan_client import TrxByHashResponse, etherscan_client, ResultResponseProxy


@pytest.mark.asyncio
async def test_get_trx_by_hash(server, config, mock_responses, generator_data):

    trx_hash = 'trx_hash'

    body = generator_data(TrxByHashResponse)
    data = ResultResponseProxy(json_rpc='2.0', id=1, result=body)
    url = URL(config.eth.url) / 'api' % {'module': 'proxy', 'action': 'eth_getTransactionByHash', 'txhash': trx_hash, 'apikey': config.eth.apikey}
    mock_responses.get(
        url=url,
        body=data.json(),
        status=status.HTTP_200_OK,
    )
    result = await etherscan_client.get_trx_by_hash(trx_hash)
    assert result
