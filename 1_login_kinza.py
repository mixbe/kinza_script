# -*- coding: UTF-8 -*-

from dotenv import dotenv_values
from eth_account import Account
from eth_account.messages import encode_structured_data
import requests
import json
from utils.read_wallets import ReadWallets

config = dotenv_values(".env")
PRIVATE_KEY = config['PRIVATE_KEY']


def build_permit_params(chain_id, referer_code):
    return {
        'types': {
            'EIP712Domain': [
                {'name': 'chainId', 'type': 'uint256'}
            ],
            'Message': [
                {'name': 'market', 'type': 'string'},
                {'name': 'content', 'type': 'string'},
                {'name': 'refererCode', 'type': 'string'}
            ],
        },
        'primaryType': 'Message',
        'domain': {
            'chainId': chain_id,
        },
        'message': {
            'market': "Kinza",
            'content': "agree to bind to a referralCode",
            'refererCode': referer_code,
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
    return signature_vrs.signature.hex()


def post_binding(signature, address, referral_code):
    url = "https://lcscsi0shg.execute-api.ap-southeast-1.amazonaws.com/referral/binding"
    payload = json.dumps({
        "signature": signature,
        "address": address,
        "referralCode": referral_code,
        "chainId": 56
    })
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


if __name__ == '__main__':
    """
    https://app.kinza.finance/#/referral?referralCode=UHZOJK
    """

    # todo The invitation code can be replaced with your own

    referer_code = 'UHZOJK'
    wallets = ReadWallets()
    for wallet in wallets.get_accounts():
        print("index: ", wallet['index'])
        typed_data = build_permit_params(56, referer_code)
        signature_vrs = get_signature_from_typed_data(wallet['privateKey'], typed_data)
        post_binding(signature_vrs, wallet['address'], referer_code)
