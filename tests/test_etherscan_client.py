import pytest
from starlette import status

from etherscan_converter.adapters.etherscan_client import etherscan_client, TrxByHashResponse


@pytest.mark.asyncio
async def test_get_current_user_from_core_success(server, config, mock_responses, generator_data):

    trx_hash = 'trx_hash'

    body = generator_data(TrxByHashResponse)

    mock_responses.get(
        f'{config.core_client.url}?module=proxy&action=eth_getTransactionByHash&txhash={trx_hash}&apikey={config.apikey}',
        body=body.json(),
        status=status.HTTP_200_OK,
    )
    result = await etherscan_client.get_current_user_from_core(trx_hash)
    assert result
