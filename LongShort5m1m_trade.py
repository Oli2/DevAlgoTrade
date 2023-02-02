import pandas as pd
import os
import sys
import yaml
import subprocess
from talib import EMA
from ib_insync import *
from SMA_Cross_ES_5m1m_event_trade import *
from datetime import datetime
import argparse
import logging

class NetworkFailure(Exception):
    pass

class MA_CrossLongShort(MA_CrossBase, NetworkFailure):
    """
    Get the data required to calculate the parameters for
    buy/sell decisions based on 5m/1m EMA cross overs
    """
    logging.getLogger(__name__)
    
    def get_data(self):
        ''' 
        Retrieve and prepare the 1 min data from IB.
        '''

        self.mes_futures_contract = Contract(secType='FUT', conId=533620623, symbol='MES',
                                             lastTradeDateOrContractMonth='20230317',
                                             multiplier='5', exchange='CME',
                                             currency='USD', localSymbol='MESH3',
                                             tradingClass='MES')
        attempts = 0
        bars_list=[]
        while True:
            if attempts == 10:
                alert = 'ERROR: 10 attempts of getting historical data failed. Restarting the script'
                #restarting itself
                
                command = f'bash {cwd}/kill_LongShort.sh'
                args = command.split(" ")
                p = subprocess.Popen(args=args)
                logger.error(alert)
                

            bars1m = ib.reqHistoricalData(
                    self.mes_futures_contract,
                    '',
                    barSizeSetting='1 min',
                    durationStr='1 D',
                    whatToShow='MIDPOINT',
                    useRTH=False,
                    formatDate=1,
                    keepUpToDate=True,
                    timeout=30, #Timeout in seconds after which to cancel the request
                                # and return an empty bar series.
                )
            bars5m = ib.reqHistoricalData(
                        self.mes_futures_contract,
                        '',
                        barSizeSetting='5 mins',
                        durationStr='1 D',
                        whatToShow='MIDPOINT',
                        useRTH=False,
                        formatDate=1,
                        keepUpToDate=True,
                        timeout=30, #Timeout in seconds after which to cancel the request
                                    # and return an empty bar series.
                    )
            bars_list = [bars1m, bars5m]
            def onBarsUpdate(bars, hasNewBar):
                pass    
            try:             
                if len(bars_list)==2:
                    for bars in bars_list:
                        bars.updateEvent += onBarsUpdate
                    raw1 = util.df(bars1m).set_index('date').dropna()
                    raw5 = util.df(bars5m).set_index('date').dropna()
                    break
                else:
                    logger.error(f'Historical Data failed to load properly')
            except AttributeError as error:
                logger.error(f'Exception Network failure raised \n{error}')
                attempts += 1
                ib.sleep(10)
            
             
        raw1.drop(['open', 'high', 'low', 'volume', 'average', 'barCount'], axis=1, inplace=True)
        raw1.rename(columns={'close': 'price'}, inplace=True)
        raw5.drop(['open', 'high', 'low', 'volume', 'average', 'barCount'], axis=1, inplace=True)
        raw5.rename(columns={'close': 'price'}, inplace=True)        
        self.data1 = raw1.dropna()
        self.data5 = raw5.dropna()
    

    def go_long(self, contract, units=1 ):
        """
        Opens long position
        
        Parameters
        ==========
        contract: specification of the future contract
        units: amount of contracts to be traded
        """
        if self.position in [-1, 0]:
            mes_order = MarketOrder('BUY', units, outsideRth=True)
            trade_buy = ib.placeOrder(contract, mes_order)
            ib.sleep(5)
            attempts=1
            while attempts < 11:
                if trade_buy.orderStatus.status == 'Filled':
                    msg = f'bought {units} unit(s) with the following:'
                    msg += f'\nOrderId: {trade_buy.orderStatus.orderId}'
                    msg += f'\nOrderStatus: {trade_buy.orderStatus.status}'
                    msg += f'\nAvgFilledPrice: {trade_buy.orderStatus.avgFillPrice}'
                    filltime = [i.time for i in trade_buy.dict().get('fills')][0]
                    msg += f'\nFillTime: {filltime}'
                    self.net_liquidation = [i.value for i in ib.accountSummary(self.account)\
                        if i.tag =='NetLiquidation' and i.currency == 'USD']
                    msg += f'\nNetLiquidation: {self.net_liquidation}'
                    pnl = self.get_PnL()
                    msg += f'\nAccount PnL:'
                    msg += f'\nDailyPnL: {[i.dailyPnL for i in pnl]}'  
                    msg += f'\nUnrealizedPnL: {[i.unrealizedPnL for i in pnl]}'
                    msg += f'\nRealizedPnL: {[i.realizedPnL for i in pnl]}'                   
                    logger.info(msg)
                    ib.sleep(5) #wait for updating the position 
                    break
                    
                else:
                    logger.error(f'Attempt: {attempts} BUY Order not filled. Check the status')
                    alert = f'Attempt: {attempts} BUY Order not filled. Check the status'   
                    if attempts == 10:
                        logger.error('send SMS notification')
                    print('!' * 100)
                    attempts += 1
                    ib.sleep(5)

    def go_short(self, contract, units=1):
        """
        Opens short position
        
        Parameters
        ==========
        contract: specification of the future contract
        units: amount of contracts to be traded
        """
        if self.position in [1,0]:
            mes_order = MarketOrder('SELL', units, outsideRth=True)
            trade_sell = ib.placeOrder(contract, mes_order)
            ib.sleep(5)
            attempts=1
            while attempts < 11:
                if trade_sell.orderStatus.status == 'Filled':
                    msg = f'sold {units} unit(s) with the following'
                    msg += f'\nOrderId: {trade_sell.orderStatus.orderId}'
                    msg += f'\nOrderStatus: {trade_sell.orderStatus.status}'
                    msg += f'\nAvgFilledPrice: {trade_sell.orderStatus.avgFillPrice}'
                    filltime = [i.time for i in trade_sell.dict().get('fills')][0]
                    msg += f'\nFillTime: {filltime}'
                    self.net_liquidation = [i.value for i in ib.accountSummary(self.account)\
                        if i.tag =='NetLiquidation' and i.currency == 'USD']
                    msg += f'\nNetLiquidation: {self.net_liquidation}'
                    pnl = self.get_PnL()
                    msg += f'\nAccount PnL:'
                    msg += f'\nDailyPnL: {[i.dailyPnL for i in pnl]}'  
                    msg += f'\nUnrealizedPnL: {[i.unrealizedPnL for i in pnl]}'
                    msg += f'\nRealizedPnL: {[i.realizedPnL for i in pnl]}'
                    logger.info(msg)
                    ib.sleep(5) #wait for updating the position 
                    break
                else:
                    logger.error(f'Attempt: {attempts} SELL Order not filled. Check the status')
                    alert = f'Attempt: {attempts} SELL Order not filled. Check the status'  
                    logger.error(alert)
                    if attempts == 10:
                        logger.error('send SMS notification') 
                    print('!' * 100)
                    attempts += 1
                    ib.sleep(5)
    def get_PnL(self):
        ib.reqPnL(self.account,'')
        ib.sleep(2)
        account_pnl = ib.pnl()
        ib.cancelPnL(self.account,'')
        return account_pnl
    
    def get_position(self):
        if len(ib.positions()) ==0:
            self.position = 0
        elif len(ib.positions()) != 0 and int(ib.positions()[0].position) in [1,-1]:
            self.position = int(ib.positions()[0].position)
        else:
            alert = f'Number of positions is {int(ib.positions()[0].position)}. Take corrective actions'
            logger.error(alert)

    def run_sma_strategy(self, SMA1, SMA2):
        """
        Prepare the data to calculate Moving averages and based on the 
        cross over signals generate sell or buy orders
        
        Parameters
        ==========
        SMA1 - fast moving average
        SMA2 - slow moving average
        """
        # self.position = 0  # initial neutral position is set up in SMA_Cross_ES_5m1m_event_trade
        self.trades = 0  # no trades yet
        self.amount = self.initial_amount  # reset initial capital

        self.data1['SMA1'] = EMA(self.data1['price'],SMA1) # 1min faster EMA for sell signals
        self.data1['SMA2'] = EMA(self.data1['price'],SMA2) # 1min slower EMA
        self.data5['SMA3'] = EMA(self.data5['price'],SMA1) # 5min faster EMA for buy signals
        self.data5['SMA4'] = EMA(self.data5['price'],SMA2) # 5min faster EMA
        
        date_format = "%Y-%m-%d %H:%M:%S"
        msg = f'\n\nTime: {datetime.now().strftime(date_format)}'
        msg += f'\nRunning SMA strategy | SMA1={SMA1} & SMA2={SMA2}'
        msg += f'\ncurrent position = {self.position}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        msg += f'\nLast data received 1m'
        msg += f'\n{self.data1.tail(1)}'
        msg += f'\n{"="*55}'
        msg += f'\nLast data received 5m'
        msg += f'\n{self.data5.tail(1)}'
        msg += f'\n{"="*55}'
        msg += f'\nposition {self.position}'
        logger.info(msg)
 
        if self.position == 0:
            if (self.data1['SMA1'][len(self.data1)-1] > self.data1['SMA2'][len(self.data1)-1]) and \
            (self.data1['SMA1'][len(self.data1)-2] < self.data1['SMA2'][len(self.data1)-2]):
                logger.info(f'SMA1 > SMA2 met and SMA1 -2 < SMA2 -2 Open long')
                self.go_long(contract = self.mes_futures_contract)
                alert = f'Algo-trade just opened a long position. Position = {self.position}'
                alert += f'\n{self.get_PnL()}'
                logger.info(alert)


        if self.position == 1:
            if self.data1['SMA1'][len(self.data1)-1] < self.data1['SMA2'][len(self.data1)-1]:
                logger.info(f'SMA1 < SAM2 - exit a long position')
                self.go_short(contract = self.mes_futures_contract) # exit long position 
                alert = f'Algo-trade just closed a long position. Position = {self.position}'
                alert += f'\n{self.get_PnL()}'
                logger.info(alert)
            else:
                logger.info(f'SMA1 > SMA2')
        if self.position == 0:
            if (self.data1['SMA1'][len(self.data1)-1] < self.data1['SMA2'][len(self.data1)-1]) and \
            (self.data1['SMA1'][len(self.data1)-2] > self.data1['SMA2'][len(self.data1)-2]):
                logger.info(f'SMA1 > SMA2 met and SMA1 -2 < SMA2 -2 Open long')
                self.go_short(contract = self.mes_futures_contract) # Reversed logic
                alert = f'Algo-trade just opened a long position. Position = {self.position}'
                alert += f'\n{self.get_PnL()}'
                logger.info(alert)
 
        if self.position == -1:
            if self.data1['SMA1'][len(self.data1)-1] > self.data1['SMA2'][len(self.data1)-1]:
                logger.info(f'SMA1 > SAM2 met - exit a short position')
                self.go_long(contract = self.mes_futures_contract)
                alert = f'Algo-trade just closed a short position. Position = {self.position}'
                alert += f'\n{self.get_PnL()}'
                logger.info(alert)
                
        self.get_position()

if __name__ == '__main__':
    
  
    def get_yaml_config() -> str:
        '''
        Read current working dir from the config.yaml file
        
        Returns:
        --------
        Absolute path to the directory where the launch script is located    
        '''
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        cwd = config['cwd']
        port = config['port']
        if 'LongShort5m1m_trade.py' in os.listdir(cwd):
            return cwd, port     
        else:
            logger.error('LongShort5m1m_trade.py not found in cwd.\
                         Check the config.yaml file ')   
    
    def get_logger() -> logging.Logger:
        '''
        Create a custom logger, handlers and formaters
        
        Return
        ======
        logger : logging.Logger
        '''
        logger = logging.getLogger(__name__)
        # default logger logging level is WARRNING. If we need to use INFO,
        # this need to be exclusively set up for both logger and handler
        logger.setLevel(logging.INFO) 
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("./logs/auto_trade.log", mode='a') # TBC Apply universal rule to path
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        
        # logs formatting
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
        file_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
             datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)
        
        #adding handlers to the logger
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_parser() -> argparse.ArgumentParser:
        '''
        Set argument parser
        
        Return
        ======
        parser: argparse.ArgumentParser
        '''
        parser = argparse.ArgumentParser(
            prog="BackTestLongShort5m1m_trade",
            description="Command line interface for BackTestLongShort5m1m_trade",
        )
        parser.add_argument(
            "-p", "--position",
            type=int,
            help=(
                "Value of position argument in BacktestLongShort class. Defaults to 0"
            ),
            default=0,
        )
        return parser
    
    def run_strategies(ib, contract):

        try:
            while (ib.isConnected()):
                ib.sleep(5) # give the time to update the self.position list before executing run_sma_strategy
                contract.get_data()
                if contract.mes_futures_contract.conId in [i.contract.conId for i in ib.positions()]:
                    for i in ib.positions():
                        if i.contract.conId == contract.mes_futures_contract.conId:
                            contract.position = int(i.position) #reads the position count from IBKR
                    logger.info(f'position read from IBKR: {lsbt.position}')
                contract.run_sma_strategy(9, 21)
        except KeyboardInterrupt:
            logger.info('Interrupted')
    
    parser = get_parser()
    args = parser.parse_args()
        
    lsbt = MA_CrossLongShort(symbol="MES_5min", amount=210000., position=args.position, ftc=0.57, verbose=False)

    logger=get_logger()
    cwd, port = get_yaml_config()
    while True:
        try: 
            ib = IB()
            if not ib.isConnected():
                ib.RequestTimeout=20 #final value TBD
                ib.connect(host='127.0.0.1', port=port, clientId=115) # TWS app or IB Gateway
                lsbt.account = ib.managedAccounts()[0] #stores the account number
                break
            else:
                logger.info('Trying to connect to the existing client')
                lsbt.account = ib.managedAccounts()[0] #stores the account number
                break
                
        except ConnectionError as error:
            logger.error('ib.connect to TWS lost',error)
            logger.error('Restarting the script')
            command = f'bash {cwd}/kill_restart_IBGateway.sh'
            args = command.split(" ")
            p = subprocess.Popen(args=args)
            ib.sleep(60)
      
    run_strategies(ib=ib, contract=lsbt)
