# -*- coding: UTF-8 -*-
import json
import time

from dotenv import dotenv_values
from eth_account import Account
from eth_account.messages import encode_structured_data
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3

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


def build_permit_params(chain_id, token, revision, token_name, owner, spender, nonce, deadline, value):
    return {
        'types': {
            'EIP712Domain': [
                {'name': 'name', 'type': 'string'},
                {'name': 'version', 'type': 'string'},
                {'name': 'chainId', 'type': 'uint256'},
                {'name': 'verifyingContract', 'type': 'address'},
            ],
            'Permit': [
                {'name': 'owner', 'type': 'address'},
                {'name': 'spender', 'type': 'address'},
                {'name': 'value', 'type': 'uint256'},
                {'name': 'nonce', 'type': 'uint256'},
                {'name': 'deadline', 'type': 'uint256'},
            ],
        },
        'primaryType': 'Permit',
        'domain': {
            'name': token_name,
            'version': revision,
            'chainId': chain_id,
            'verifyingContract': token,
        },
        'message': {
            'owner': owner,
            'spender': spender,
            'value': value,
            'nonce': nonce,
            'deadline': deadline,
        },
    }


def get_signature_from_typed_data(private_key, typed_data):
    signable_msg_from_dict = encode_structured_data(typed_data)
    signature_vrs = Account.sign_message(signable_msg_from_dict, private_key)
    return signature_vrs


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

        functions = web3.eth.contract(address=GATEWAY_V3, abi=gatewayv3_abi).functions
        tx = functions.withdrawETHWithPermit(
            LP_TOKEN,
            balance,
            account.address,
            EXPIRY_TIMESTAMP,
            signature_vrs.v,
            HexBytes(signature_vrs.r),
            HexBytes(signature_vrs.s)
        ).build_transaction({
            'from': Web3.to_checksum_address(account.address),
            'nonce': web3.eth.get_transaction_count(Web3.to_checksum_address(account.address)),
            'gasPrice': web3.eth.gas_price,
            'value': 0
        })

    tx['gas'] = web3.eth.estimate_gas(tx)
    tx_create = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Tx successful with hash: {tx_receipt.transactionHash.hex()}")
