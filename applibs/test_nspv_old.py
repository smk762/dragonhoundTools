#!/usr/bin/env python3
import os
import sys
import csv
import json
import time
import shutil
import requests
import itertools
import subprocess
import datetime
from pprint import pprint
from os.path import expanduser
from urllib.parse import urlparse
from nspvlib import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'qa'))
from qalib import *
local_ip = "http://127.0.0.1:7777"
userpass = 'userpass'

# params list format [no value (false), good value, bad value]
wif = [False, 'UrJUbSqsb1chYxmQvScdnNhVc2tEJEBDUPMcxCCtgoUYuvyvLKvB', 'thiswontwork']
height = [False, 777, 'notnum']
prevheight = [False, 765, 'notnum']
nextheight = [False, 785, 'notnum']
address = [False, 'RYPzyuLXdT9JYn7pemYaX3ytsY3btyaATY', 'not_an_addr']
isCCno = [False, 0, 'notnum']
isCCyes = [False, 1, 'notnum']
skipcount = [False, 2, 'notnum']
txfilter = ['not implemented yet']
amount = [False, 2, 'notnum']
txid = [False, 'f261773a389445100d8dfe4fc0b2d9daeaf90ef6264435e739fbd698624b77d6', 'not_txid']
vout = [False, 1,'d']
rawhex = [False, '', 'nothex']

nspv_header_row = ['METHOD', 'RESULT', 'PARAMS']

nspv_methods = {'broadcast':[rawhex],
                'getnewaddress':[],
                'getpeerinfo':[],
                'hdrsproof':[prevheight,nextheight],
                'help':[],
                'listtransactions1':[address,isCCno,skipcount],
                'listtransactions2':[address,isCCyes,skipcount],
                'listunspent1':[address,isCCno,skipcount],
                'listunspent2':[address,isCCyes,skipcount],
                'login':[wif], 'logout':[], 'mempool':[],
                'notarizations':[height],
                'spend':[address,amount],
                'spentinfo':[txid,vout],
                'txproof':[txid,height],
                'stop':[]}


repo_path = build_commit('nspv')

csv_filename = get_csv_filename('nspv_rpc', repo_path)
#app_test_date_commit
csv_filename = "KMD_"+csv_filename
#outcome_base_app_test_date_commit
with open(csv_filename, 'w+') as csvFile:
  writer = csv.writer(csvFile,
                      delimiter=',',
                      quotechar='"',
                      quoting=csv.QUOTE_ALL)
  writer.writerow(nspv_header_row)
  csvFile.flush()

  for method in nspv_methods:
    param_lists = []
    for param_list in nspv_methods[method]:
      param_lists.append(param_list)
    test_params = list(itertools.product(*param_lists))
    for x in test_params:
      csv_row = []
      print("nspv_"+method+str(x))
      if method == 'broadcast':
        resp = nspv_broadcast(local_ip, userpass, *x)
      elif method == 'getnewaddress':
        resp = nspv_getnewaddress(local_ip, userpass, *x)
      elif method == 'getpeerinfo':
        resp = nspv_getpeerinfo(local_ip, userpass, *x)
      elif method == 'hdrsproof':
        resp = nspv_hdrsproof(local_ip, userpass, *x)
      elif method == 'help':
        resp = nspv_help(local_ip, userpass, *x)
      elif method == 'listtransactions1':
        resp = nspv_listtransactions(local_ip, userpass, *x)
      elif method == 'listtransactions2':
        resp = nspv_listtransactions(local_ip, userpass, *x)
      elif method == 'listunspent1':
        resp = nspv_listunspent(local_ip, userpass, *x)
      elif method == 'listunspent2':
        resp = nspv_listunspent(local_ip, userpass, *x)
      elif method == 'login':
        resp = nspv_login(local_ip, userpass, *x)
      elif method == 'notarizations':
        resp = nspv_notarizations(local_ip, userpass, *x)
      elif method == 'spend':
        resp = nspv_spend(local_ip, userpass, *x)
      elif method == 'spentinfo':
        resp = nspv_spentinfo(local_ip, userpass, *x)
      elif method == 'stop':
        pass
        #resp = nspv_stop(local_ip, userpass, *x)
      elif method == 'txproof':
        resp = nspv_txproof(local_ip, userpass, *x)
      try:
        result = resp.json()
      except:
        result = resp.text
        pass
      time.sleep(2)
      print(result)
      csv_row.append(method)
      csv_row.append(result)
      csv_row.append(str(*x))
      writer.writerow(csv_row)
outcome = 'Completed'
nspv_stop(local_ip, userpass)
csvFile.close()
os.rename(csv_filename, outcome+"_"+csv_filename)
