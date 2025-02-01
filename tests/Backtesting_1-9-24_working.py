import pandas as pd
import pandas_ta as ta
from DP_Strategies import LSimpleStrategy1, SSimpleStrategy1
from DP_Indicators import Expand_1minute_Data, StockData
import time



def process_bars(HistBeginDateTime, HistEndDateTime, df, df5, df15):
    global total_gain
    begin_datetime = pd.to_datetime(HistBeginDateTime)
    end_datetime = pd.to_datetime(HistEndDateTime)

    stock_data_1 = StockData()
    stock_data_5 = StockData()
    stock_data_15 = StockData()
    stock_data_1.load_data(df)  # update class with latest stock data values
    stock_data_5.load_data(df5)  # update class with latest stock data values
    stock_data_15.load_data(df15)  # update class with latest stock data values

    # Iterate through rows within the specified time range, and call strategies
    for index, row in df.loc[begin_datetime:end_datetime].iterrows():
        foo = LSimpleStrategy1(False, index, stock_data_1, stock_data_5, stock_data_15)
        foo = SSimpleStrategy1(False, index, stock_data_1, stock_data_5, stock_data_15)



