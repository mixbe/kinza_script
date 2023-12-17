# -*- coding: UTF-8 -*-


import json
import os
import sys

from eth_account import Account

root_dir = os.path.dirname(os.path.abspath(__file__))


def saveETHWallet(jsonData):
    with open(root_dir + '/../accounts/wallets.json', 'w') as f:
        json.dump(jsonData, f, indent=4)


def createNewETHWallet(number):
    wallets = []
    for id in range(number):
        # 添加一些随机性
        account = Account.create('zksync Random  Seed' + str(id))
        # 私钥
        privateKey = account._key_obj
        # 公钥
        publicKey = privateKey.public_key
        # 地址
        address = publicKey.to_checksum_address()
        wallet = {
            "index": id,
            "address": address,
            "privateKey": str(privateKey)
        }
        wallets.append(wallet)

    return wallets


if __name__ == '__main__':
    numbers = 100
    if len(sys.argv) == 2:
        numbers = int(sys.argv[1])
    wallets = createNewETHWallet(numbers)
    saveETHWallet(wallets)
