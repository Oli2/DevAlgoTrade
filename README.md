# DevAlgoTrade
Development of TWS Algorithmic Futures Trading bot
## Running the application
The main script LongShort5m1m_trade.py, will launch the application. 
It works with IBKR using [in_sync](https://github.com/erdewit/ib_insync) library (IBRK API wrapper).
To establish the data connetivity, first launch the IB Gateway or TWS app and login to a paper account.
### Updating config.yaml
Once you have cloned the repository to your local machine, please update the config.yaml file with:
 - cwd: directory on your local machine where LongShort5m1m_trade.py scripts resides. 
 - port: port on which the IB Gateway or TWS application (they should be on the same network) is listening.
### Updating the kill_restart_IBGateway.sh
This script kills and restart the process responsible for running IB Gateway or TWS application.
Please make shure that both `kill` and `nohup` commands have got respective paths/filenames specific to your system.  
In the default configuration:  
 `kill $(ps aux | grep displaybannerandlaunch.sh | grep -v grep | awk '{print $2}')`  
`grep displaybannerandlaunch.sh` identifies a process responsible for running IB Gateway.  
`nohup bash /Users/tomcheckiewics/Applications/IBC/IBCMacos-3.15.2/gatewaystartmacos.sh`  restars the IB Gateway.


