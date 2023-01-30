#!/bin/bash


# This script uses bash kill command to terminate the main AlgoTrader python script 
# The path is specific to an individual system and needs to be updated accordingly


kill `ps aux |grep LongShort5m1m_trade.py | grep -v grep |awk '{print $2}'`

