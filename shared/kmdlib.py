#!/usr/bin/env python3
import os
import re
import sys
import json
import http
import time
import codecs
import requests
import platform
from slickrpc import Proxy
from os.path import expanduser
 
# Get and set config
cwd = os.getcwd()
home = expanduser("~")

addr_config = home+"/DragonhoundTools/config/test_addr.json"
launch_config = home+"/DragonhoundTools/config/launch_params.json"

# Get Address configs
try:
    with open(addr_config) as addr_j:
        addr_json = json.load(addr_j)
except:
    print("No test_addr.json file!")
    print("Create one using the template:")
    print("cp "+home+"/DragonhoundTools/config/test_addr_example.json "+home+"/DragonhoundTools/config/test_addr.json")
    print("nano "+home+"/DragonhoundTools/config/test_addr.json")

# Get launch param configs
try:
    with open(launch_config) as launch_j:
        launch_json = json.load(launch_j)
except:
    print("No launch_params.json file!")
    print("Create one using the template:")
    print("cp "+home+"/DragonhoundTools/config/launch_params_example.json "+home+"/DragonhoundTools/config/launch_params.json")
    print("nano "+home+"/DragonhoundTools/config/launch_params.json")
    
try:
    with open(home+"/DragonhoundTools/config/config.json") as j:
        config_json = json.load(j)
except:
    print("No config.json file!")
    print("Create one using the template:")
    print("cp "+home+"/DragonhoundTools/config/config_example.json "+home+"/DragonhoundTools/config/config.json")
    print("nano "+home+"/DragonhoundTools/config/config.json")

try:
    this_node = config_json['this_node']
    pubkey = config_json['pubkey']
    iguanaport = config_json['iguanaport']
    # set node specific coins config
    ntx_Radd = config_json['ntx_Radd']
    nn_Radd = config_json['nn_Radd']
    stats_oracletxid = config_json['stats_oracleid']
    if this_node == 'primary':
        komodo_ac_json = config_json['komodo_ac_json']
        coins_json = home+'/'+komodo_ac_json
    elif this_node == 'third_party':
        third_party_json = config_json['third_party_json']
        coins_json = home+'/'+third_party_json
    elif this_node == 'labs':
        labs_ac_json = config_json['labs_ac_json']
        coins_json = home+'/'+labs_ac_json
    else:
        komodo_ac_json = config_json['komodo_ac_json']
        coins_json = home+'/'+komodo_ac_json
except Exception as e:
    print("config.json file needs an update!")
    print(e)
    print("nano "+home+"/DragonhoundTools/config/config.json")
sweep_Radd = config_json['sweep_Radd']
j.close()

third_party_cointags = ['GAME', 'EMC2']

# Set coin config locations. Not yet tested outside Linux for 3rd party coins!
operating_system = platform.system()
if operating_system == 'Darwin':
    ac_dir = home + '/Library/Application Support/Komodo'
elif operating_system == 'Linux':
    ac_dir = home + '/.komodo'
elif operating_system == 'Win64' or operating_system == 'Windows':
    ac_dir = '%s/komodo/' % os.environ['APPDATA']
    import readline


def colorize(string, color):
    colors = {
                'black':'\033[30m',
                'red':'\033[31m',
                'green':'\033[32m',
                'orange':'\033[33m',
                'blue':'\033[34m',
                'purple':'\033[35m',
                'cyan':'\033[36m',
                'lightgrey':'\033[37m',
                'darkgrey':'\033[90m',
                'lightred':'\033[91m',
                'lightgreen':'\033[92m',
                'yellow':'\033[93m',
                'lightblue':'\033[94m',
                'pink':'\033[95m',
                'lightcyan':'\033[96m',
        }
    if color not in colors:
        return string
    else:
        return colors[color] + string + '\033[0m'

def def_creds(chain):
    rpcport =''
    coin_config_file = ''
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    elif chain == 'BTC':
        coin_config_file = str(home + '/.bitcoin/bitcoin.conf')
    elif this_node == 'third_party':
        with open(coins_json) as file:
            coins_3p = json.load(file)
        for coin in coins_3p:
            if coin['tag'] == chain:
                coin_config_file = str(home+'/'+coin['datadir']+'/'+coin['conf'])
        if coin_config_file == '':
            coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')                
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        elif chain == 'KMD':
            rpcport = 8333
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)
    return(Proxy("http://%s:%s@127.0.0.1:%d"%(rpcuser, rpcpassword, int(rpcport))))

def coins_info(coins_json, attrib='ac_name'):
        infolist = []
        if this_node == 'third_party' and attrib == 'ac_name':
            attrib='tag'
        with open(coins_json) as file:
            assetchains = json.load(file)
        for chain in assetchains:
            infolist.append(chain[attrib])
        return infolist

def is_chain_synced(chain):
    rpc_connection = def_credentials(chain)
    getinfo_result = rpc_connection.getinfo()
    blocks = getinfo_result['blocks']
    longestchain = getinfo_result['longestchain']
    if blocks == longestchain:
        return(0)
    else:
        return([blocks, longestchain])

def importprivkey_since(coin, blocks_back):
    rpc[coin].importprivkey("", "", True, blocks_back)

def wait_confirm(coin, txid):
    start_time = time.time()
    mempool = rpc[coin].getrawmempool()
    while txid in mempool:
        print(colorize("Waiting for "+txid+" confirmation...",'orange'))
        time.sleep(60)
        mempool = rpc[coin].getrawmempool()
        #print(mempool)
        looptime = time.time() - start_time
        if looptime > 900:
            print(colorize("Transaction timed out",'red'))
            return False
    print(colorize("Transaction "+txid+" confirmed!",'green'))
    return True

def wait_notarised(coin, txid):
    start_time = time.time()
    status = rpc[coin].gettransaction(txid)['confirmations']
    while status != 1:
        looptime = time.time() - start_time
        print("Waiting for notarisation..."+str(looptime)+" sec")
        time.sleep(30)
        status = rpc[coin].gettransaction(txid)['confirmations']
    print("Transaction "+txid+" notarisated!")
    return True

def send_confirm_rawtx(coin, hexstring):
    start_time = time.time()
    txid = rpc[coin].sendrawtransaction(hexstring)
    while len(txid) != 64:
        print("Sending raw transaction...")
        txid = rpc[coin].sendrawtransaction(hexstring)
        time.sleep(30)
        looptime = time.time() - start_time
        if looptime > 900:
            print("Transaction timed out")
            print(txid)
            exit(1)
    while txid in rpc[coin].getrawmempool():
        looptime = time.time() - start_time
        print("Waiting for confirmation, "+str(looptime)+" sec")
        time.sleep(30)
        if looptime > 900:
            print("Transaction timed out")
            print(rpc[coin].getrawmempool())
            print(rpc[coin].getblockcount())
            exit(1)
    print("Transaction "+txid+" confirmed!")
    return txid

    
def unlockunspent(coin):
        unspent = rpc[coin].listlockunspent()
        rpc[coin].lockunspent(True, unspent)

def unspent_count(coin):
    count = 0
    dust = 0
    if coin in third_party_cointags:
        ntx_utxo_size = 0.001
    else:
        ntx_utxo_size = 0.0001
    unspent = rpc[coin].listunspent()
    for utxo in unspent:
        if utxo['amount'] == ntx_utxo_size:
            count += 1
        elif utxo['amount'] < ntx_utxo_size:
            dust += 1
    return [count,dust]

def unspent_info(coin):
    count = 0
    dust = 0
    newest = 999999999999999999
    oldest = 0
    interest_utxos = 0 
    interest_value = 0
    if coin in third_party_cointags:
        ntx_utxo_size = 0.001
    else:
        ntx_utxo_size = 0.0001
    unspent = rpc[coin].listunspent()
    for utxo in unspent:
        if utxo['interest'] > 0:
            interest_utxos += 1
            interest_value += utxo['interest']        
        if utxo['confirmations'] > oldest:
            oldest = time_since
        if utxo['confirmations'] < newest:
            newest = time_since
        if utxo['amount'] > largest:
            oldest = time_since
        if utxo['amount'] < smallest:
            newest = time_since
        if utxo['amount'] == ntx_utxo_size:
            count += 1
        elif utxo['amount'] < ntx_utxo_size:
            dust += 1
    return [count,dust,oldest,newest,interest_utxos,interest_value]

def unspent_interest(coin):
    interest_utxos = 0 
    interest_value = 0
    unspent = rpc[coin].listunspent()
    for utxo in unspent:
        if utxo['interest'] > 0:
            interest_utxos += 1
            interest_value += utxo['interest']
    return [interest_utxos,interest_value]

# get coins list
coinlist = []
if this_node == 'third_party':
    attrib='tag'
else:
    attrib = 'ac_name'
with open(coins_json) as file:
    assetchains = json.load(file)
for chain in assetchains:
    coinlist.append(chain[attrib])
if this_node != 'third_party':
    coinlist.append('KMD')

intervals = (
    ('d', 86400),
    ('hr', 3600),
    ('min', 60),
    ('sec', 1),
    )

def display_time(seconds, granularity=1):
    result = []
    if seconds > 604800:
        time_str = "> week!"
    else:
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(int(value) , name))
        time_str = ', '.join(result[:granularity])
    return time_str



# Set RPCs
rpc = {}
coinlist.append('ORACLEARTH')
if this_node == 'primary':
    coinlist.append('BTC')
for coin in coinlist:
    try:
        rpc[coin] = def_creds(coin)
    except Exception as e:
        print("RPCs Error: "+str(e))
        pass

def z_sendmany_twoaddresses(coin, src_addr, recepient1, amount1, recepient2, amount2):
    str_sending_block = "[{{\"address\":\"{}\",\"amount\":{}}},{{\"address\":\"{}\",\"amount\":{}}}]".format(recepient1, amount1, recepient2, amount2)
    sending_block = json.loads(str_sending_block)
    opid = rpc[coin].z_sendmany(src_addr,sending_block)
    return opid


def opid_to_txid(coin, opid):
    str_sending_block = "[\"{}\"]".format(opid)
    sending_block = json.loads(str_sending_block)
    opid_json = rpc[coin].z_getoperationstatus(sending_block)
    opid_dump = json.dumps(opid_json)
    opid_dict = json.loads(opid_dump)[0]
    try:
        txid = opid_dict['result']['txid']
    except Exception as e:
        print(e)
        print(opid_dict)
    return txid
