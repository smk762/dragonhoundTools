#!/bin/bash
cd
cd komodo
git pull
cd
cd dPoW
git pull
pkill -9 iguana
source ~/komodo/src/pubkey.txt
cd ~/komodo/src
./komodod -notary -pubkey=$pubkey -opretmintxfee=0.004 -minrelaytxfee=0.000035 &
sleep 300
bitcoind -deprecatedrpc=estimatefee &
sleep 300
~/VerusCoin/src/verusd -pubkey=$pubkey &
sleep 60
./assetchains
#./assetchains
komodo-cli setgenerate true 1
cd ~/dPoW/iguana
#./m_notary
./m_notary_KMD


