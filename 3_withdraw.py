# -*- coding: UTF-8 -*-
import json
import time

from dotenv import dotenv_values
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from utils.contract_helpers import build_permit_params, get_signature_from_typed_data

config = dotenv_values(".env")

BSC_NODE_URL = config['BSC_NODE_URL']

PRIVATE_KEY = config['PRIVATE_KEY']
account: LocalAccount = Account.from_key(PRIVATE_KEY)

# Expiry timestamp
EXPIRY_TIMESTAMP = int(time.time()) + 3600

GATEWAY_V3 = '0xCC650b486f723C924370656b509a82bD69526739'
# LP toekn
LP_TOKEN = '0xf5e0ADda6Fb191A332A787DEeDFD2cFFC72Dba0c'


def get_erc20_instance(w3, address):
    with open('abi/ERC20.abi', 'r') as file:
        erc20_abi = json.load(file)
    return w3.eth.contract(address=address, abi=erc20_abi)


if __name__ == '__main__':
    """
    Remove liquidity 
    """

    web3 = Web3(Web3.HTTPProvider(BSC_NODE_URL))

    lp_token = get_erc20_instance(web3, LP_TOKEN)
    balance = lp_token.functions.balanceOf(account.address).call()
    print(f"LP balance: {web3.from_wei(balance, 'ether'):.18f} ether")
    if balance < 100:
        print("Insufficient balance does not need to be executed !!!")
        exit(1)

    # build permit params
    typed_data = build_permit_params(web3.eth.chain_id, LP_TOKEN, '1',
                                     lp_token.functions.name().call(),
                                     account.address,
                                     GATEWAY_V3,
                                     lp_token.functions.nonces(account.address).call(),
                                     EXPIRY_TIMESTAMP,
                                     balance)

    # get signature from typed data
    signature_vrs = get_signature_from_typed_data(PRIVATE_KEY, typed_data)

    # print("Generated Permit Signature v:", signature_vrs.v)
    # print("Generated Permit Signature r:", hex(signature_vrs.r))
    # print("Generated Permit Signature s:", hex(signature_vrs.s))

    with open('abi/WrappedTokenGatewayV3.abi', 'r') as file:
        gatewayv3_abi = json.load(file)

        tx = web3.eth.contract(address=GATEWAY_V3, abi=gatewayv3_abi).functions.withdrawETHWithPermit(
            LP_TOKEN,
            balance,
            account.address,
            EXPIRY_TIMESTAMP,
            signature_vrs.v,
            hex(signature_vrs.r),
            hex(signature_vrs.s)
        ).build_transaction({
            'from': Web3.to_checksum_address(account.address),
            'nonce': web3.eth.get_transaction_count(Web3.to_checksum_address(account.address)),
            'gasPrice': web3.eth.gas_price,
            'value': 0
        })
        tx_create = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Tx successful with hash: {tx_receipt.transactionHash.hex()}")
