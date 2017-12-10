import sqlite3
import pandas as pd
import numpy as np
from sklearn import linear_model



# returns names of all existing tables in db
def get_table_names(db_name):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        t = [x[0] for x in c.execute("SELECT name FROM "
                                     "sqlite_master WHERE type='table';").fetchall()]
        t.sort()
        return t   

# returns specific table. Returns pandas DataFrame
def get_table(db_name, table_name, period=''):
    with sqlite3.connect(db_name) as conn:
        if period != '':
            period = " LIMIT " + str(period)
        return pd.read_sql_query('SELECT * FROM (SELECT * FROM %s ORDER BY timerecord DESC %s) ORDER BY timerecord ASC;' %(table_name.upper(), period), conn)

# returns table columns 
def get_table_columns(db_name):
    with sqlite3.connect(db_name) as conn:
        return list(pd.read_sql_query('PRAGMA table_info(%s);' % (get_table_names(db_name)[0]), conn).name)
	
	
	
	
	
	

	
	
	
	
#imitates trading 	
#use two methods - buy() and sell()
#self.stat returns pd.DataFrame with every trade info
class Transact:
    
    def __init__(self, amount = 0):
        self.amount = amount
        self.trade_id = 0
        self.lastbuyprice = 0
        self.lastsellprice = 0
        self.count_of_stoploss = 0
        self.switch = 0
        self.stat = pd.DataFrame([], columns = ['t_id', 'type', 'price', 'time', 'count', 'amount'])


    def buy(self, buyprice, timerecord, count=1):
        self.switch = -1
        self.trade_id += 1
        self.amount = self.amount - count
        #add stat to the stattable
        self.stat.loc[len(self.stat)] = [self.trade_id, 'buy', buyprice, timerecord, count * 0.9975, self.amount]
        self.lastbuyprice = buyprice
        
        
    
    def sell(self, sellprice, timerecord, type_='sell'):
        self.switch = 1
        sellcount = sellprice * self.stat['count'].values[-1] / self.lastbuyprice * .9975
        self.amount += sellcount
        self.lastsellprice = sellprice
        self.stat.loc[len(self.stat)] = [self.trade_id, type_, sellprice, timerecord, sellcount, self.amount]
        if type_ == 'stoploss':
            self.count_of_stoploss += 1
			
			
			
			
			
# returns bollinger bands statistics for series - lower band, mean			
def bollinger_bands(values, n, std_coef):
    if not isinstance(values, pd.core.series.Series):
        values = pd.Series(values)
    rolling_mean = values.rolling(window=n,center=False).mean()
    rolling_std = values.rolling(window=n,center=False).std()
    #upper_band = rolling_mean + rolling_std * std_coef
    lower_band = rolling_mean - rolling_std * std_coef
    return {'lower_band': lower_band, 'std': rolling_std}
