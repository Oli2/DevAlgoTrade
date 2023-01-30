#!/bin/bash


# This script uses bash kill command to terminate the IB Gateway run by IB Controller (IBC)
# or the directly the IB Gateway process if IBC is not used.  
# The path to displaybannerandlaunch.sh is specific to an individual system and needs to be updated accordingly 


kill $(ps aux | grep displaybannerandlaunch.sh | grep -v grep | awk '{print $2}');

# restarting the IB gateway
#the below line launches the IB Gatawey through IBC controller.
#if the IBC is not used this should point to IB Gateway executable.
nohup bash /Users/tomcheckiewics/Applications/IBC/IBCMacos-3.15.2/gatewaystartmacos.sh
