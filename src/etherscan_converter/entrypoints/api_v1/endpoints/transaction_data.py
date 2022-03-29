import json

from web3 import Web3
from fastapi import APIRouter
from starlette import status

from etherscan_converter.adapters.etherscan_client import etherscan_client
from etherscan_converter.entrypoints.api_v1.schemas import TrxDataResponse

router = APIRouter()

TRXHASH = '0x14dc5b46f607e2f0594bc633a50c1218f38f65216aaf3e9296f14bfa38fc3bc1'

provider = Web3.HTTPProvider('https://mainnet.infura.io/v3/02a5d9b951bd47dfbe40edaecafb3189')


@router.get(
    '/',
    summary='Get transaction data',
    responses={
        status.HTTP_200_OK: {'model': TrxDataResponse, 'description': 'Сервис работает'},
    },
)
async def get_trx_data_by_hash(trx_hash: str) -> TrxDataResponse:
    resp_trx = await etherscan_client.get_trx_by_hash(trx_hash)
    resp_contract = await etherscan_client.get_abi(resp_trx.result.to)
    resp_source_code = await etherscan_client.get_source_code_contract(resp_trx.result.to)
    w3 = Web3(provider)
    addr_contr = Web3.toChecksumAddress(resp_trx.result.to)
    trx = w3.eth.get_transaction(trx_hash)
    contract = w3.eth.contract(address=addr_contr, abi=resp_contract.result)
    input_data = contract.decode_function_input(resp_trx.result.input)
    receipt = w3.eth.get_transaction_receipt(trx_hash)

    cva = contract.events.ControlVariableAdjustment().processReceipt(receipt)
    bc = contract.events.BondCreated().processReceipt(receipt)
    bpc = contract.events.BondPriceChanged().processReceipt(receipt)
    br = contract.events.BondRedeemed().processReceipt(receipt)
    olympus_fee = contract.functions.currentOlympusFee().call()

    last_decay = contract.functions.lastDecay().call()
    debt_decay = contract.functions.debtDecay().call()
    max_payout = contract.functions.maxPayout().call()
    policy = contract.functions.policy().call()
    terms = contract.functions.terms().call()
    total_pr_bonded = contract.functions.totalPrincipalBonded().call()

    return terms