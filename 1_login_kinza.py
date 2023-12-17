# -*- coding: UTF-8 -*-
from dotenv import dotenv_values
from eth_account.messages import encode_defunct
from web3.auto import w3

config = dotenv_values(".env")
PRIVATE_KEY = config['PRIVATE_KEY']

if __name__ == '__main__':
    """
        
    https://app.kinza.finance/#/referral?referralCode=UHZOJK
    """
    msg = r"""Market: 
Kinza
Content: 
agree to bind to a referralCode
RefererCode: 
UHZOJK"""
    print(msg)
    message = encode_defunct(text=msg)
    signed_message = w3.eth.account.sign_message(message, private_key=PRIVATE_KEY)
    print(signed_message.signature.hex())
