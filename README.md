# DevAlgoTrade
Development of TWS Algorithmic Futures Trading bot
### Setting up conda environment
Please execute `conda env create --file environment.yaml` to build your local conda environment for the project.

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
`nohup bash /Users/tomcheckiewics/Applications/IBC/IBCMacos-3.15.2/gatewaystartmacos.sh`  restarts IBC and consequently IB Gateway.

### Running the application
Pre-requisites:
- project conda environment built and activated
- IBC/IB Gataway properly configured and up & running 
- config.yaml file updated with the project specific data (cwd, port)
- kill_restart_IBGateway.sh updated with the respective paths
To run the script execute the following command in the terminal:

`python LongShort5m1m_trade.py`

The main script `LongShort5m1m_trade.py`, connects with IBKR servers using [in_sync](https://github.com/erdewit/ib_insync) library (IBRK API wrapper).
To establish the data connectivity, make sure you first launch the IB Gateway or TWS app and login to a paper account. 
This implementation is utilizing [IBC](https://github.com/IbcAlpha/IBC/tree/3.15.2). IBC automates many aspects of running Interactive Brokers Trader Workstation and Gateway that would otherwise involve manual intervention. 