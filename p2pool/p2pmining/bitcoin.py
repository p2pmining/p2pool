from __future__ import division

import json
from bitcoinrpc import authproxy as bitcoinRPC
import pprint

class Bitcoin:
    def __init__(self,args):
        url = '%s://%s:%s@%s:%i' % ('https' if args.bitcoind_rpc_ssl else 'http',args.bitcoind_rpc_username,args.bitcoind_rpc_password,args.bitcoind_address, args.bitcoind_rpc_port)
        self.bitcoind = bitcoinRPC.AuthServiceProxy(url)
        
    def get_reward_transaction(self,blockhash,address):
        block = self.bitcoind.getblock(blockhash)
        amount = 0
        rtx = None
        for txid in block['tx']:
            tx = self.bitcoind.getrawtransaction(txid,1)
            if tx['vin'][0]['coinbase'] is not None:
                for vout in tx['vout']:
                    if ('xxx' if 'addresses' not in vout['scriptPubKey'] else vout['scriptPubKey']['addresses'][0]) == address:
                        amount = vout['value']
                        rtx = txid
                break
        return rtx, amount
    
    def get_transaction(self,txid):
        return self.bitcoind.getrawtransaction(txid,1)

