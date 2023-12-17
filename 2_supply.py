# -*- coding: UTF-8 -*-
import json

from dotenv import dotenv_values
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3

config = dotenv_values(".env")
BSC_NODE_URL = config['BSC_NODE_URL']

PRIVATE_KEY = config['PRIVATE_KEY']
account: LocalAccount = Account.from_key(PRIVATE_KEY)

# Contract Address
GATEWAY_V3 = '0xCC650b486f723C924370656b509a82bD69526739'
WBNB = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'

if __name__ == '__main__':
    """
    Add liquidity (BNB)
    """
    amout = 0.01
    web3 = Web3(Web3.HTTPProvider(BSC_NODE_URL))

    # Just use one account to test and you can be operated in batches
    with open('abi/WrappedTokenGatewayV3.abi', 'r') as file:
        gatewayv3_abi = json.load(file)
        tx = web3.eth.contract(address=GATEWAY_V3, abi=gatewayv3_abi).functions.depositETH(
            WBNB, account.address,
            0).build_transaction({
            'from': Web3.to_checksum_address(account.address),
            'nonce': web3.eth.get_transaction_count(Web3.to_checksum_address(account.address)),
            'gasPrice': web3.eth.gas_price,
            'value': web3.to_wei(amout, 'ether')
        })
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx_create = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Tx successful with hash: {tx_receipt.transactionHash.hex()}")
