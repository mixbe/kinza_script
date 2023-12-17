# -*- coding: UTF-8 -*-

from eth_account import Account
from eth_account.messages import encode_structured_data


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
    """
    Refer to： https://eth-account.readthedocs.io/en/stable/eth_account.html#eth_account.messages.encode_structured_data
    :param private_key:
    :param typed_data:
    :return:
    """

    signable_msg_from_dict = encode_structured_data(typed_data)
    signature_vrs = Account.sign_message(signable_msg_from_dict, private_key)
    return signature_vrs
