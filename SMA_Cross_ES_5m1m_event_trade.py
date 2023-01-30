import pandas as pd
import numpy as np
from ib_insync import *
# from pylab import mpl, plt
# plt.style.use('seaborn')
# mpl.rcParams['font.family'] = 'serif'
# util.startLoop()  # only use in interactive environments
# (i.e. Jupyter Notebooks)


class MA_CrossBase(object):
    ''' Base class for event-based backtesting of trading strategies.
    
    Attributes
    ==========
    symbol: str
        TR RIC (financial instrument) to be used
    amount: float
        amount to be invested either once or per trade
    ftc: float
        fixed transaction costs per trade (buy or sell)
    ptc: float
        proportional transaction costs per trade (buy or sell)
        
    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    plot_data:
        plots the closing price for the symbol
    get_date_price:
        returns the date and price for the given bar
    print_balance:
        prints out the current (cash) balance
    print_net_wealth:
        prints out the current net wealth
    '''
    def __init__(self, amount, position = 0,symbol = 'ES_5min',
                 ftc=0.0, ptc=0.0, verbose=True):
        self.symbol = symbol
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.units = 0
        self.position = position
        self.trades = 0
        self.verbose = verbose
        self.mes_futures_contract = None
        self.data1=None
        self.data5=None
        self.account = None
        self.net_liquidation = None

    

    def get_date_price(self, bar): #Not used at the moment
        ''' Return date and price for bar.
        not in use at the moment
        '''
        date = str(self.data.index[bar])[:19]
        price = self.data.price.iloc[bar]
        return date, price

    def print_balance(self, bar): #Not used at the moment
        ''' Print out current cash balance info.
        '''
        date, price = self.get_date_price(bar)
        print(f'{date} | current balance {self.amount:.2f}')

    def print_net_wealth(self, bar): #Not used at the moment
        ''' Print out current cash balance info.
        '''
        date, price = self.get_date_price(bar) #Not used at the moment
        net_wealth = self.units * price + self.amount
        print(f'{date} | current net wealth {net_wealth:.2f}')
