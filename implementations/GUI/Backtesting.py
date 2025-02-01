import pandas as pd
import pandas_ta as ta
from DP_Strategies import LSimpleStrategy1
from DP_Strategies import SSimpleStrategy1
from DP_Indicators import Expand_1minute_Data, StockData
import time


def process_bars(HistBeginDateTime, HistEndDateTime, df, df5, df15):
    global ltotal_gain, stotal_gain
    from globals import (PlotOutputStd, PlotOutputHA, BackTest, LiveTradeActive,
                         Ticker, HistBeginDateTime, HistEndDateTime, in_long, in_short,
                         sentry_price, sexit_price, strade_gain, UseOptimizer,
                         lentry_price, lexit_price, ltrade_gain)

    begin_datetime = pd.to_datetime(HistBeginDateTime)
    end_datetime = pd.to_datetime(HistEndDateTime)

    ltotal_gain = 0
    stotal_gain = 0

    bars1 = StockData()
    bars5 = StockData()
    bars15 = StockData()
    bars1.load_data(df)  # update class with latest stock data values
    bars5.load_data(df5)  # update class with latest stock data values
    bars15.load_data(df15)  # update class with latest stock data values

    #print('In Process')

    booty_df=pd.DataFrame( columns=['i', 'LGain', 'SGain'])

    if UseOptimizer:
        #iterate for optimizer variable 1
        for i in range(90,101,1):

            in_long = False
            in_short = False
            lentry_price = 0
            lexit_price = 0
            ltrade_gain = 0
            ltotal_gain = 0
            sentry_price = 0
            sexit_price = 0
            strade_gain = 0
            stotal_gain = 0
            LTotalGain = 0
            STotalGain = 0

            # Iterate through rows within the specified time range, and call strategies
            for index, row in df.loc[begin_datetime:end_datetime].iterrows():
                LTotalGain += LSimpleStrategy1(False, index, i, bars1, bars5, bars15)
                STotalGain += SSimpleStrategy1(False, index, i, bars1, bars5, bars15)

                # Append the values to booty_df, for analysis and optimization
                booty_df = pd.concat([booty_df, pd.DataFrame({'i': [i], 'LGain': [LTotalGain], 'SGain': [STotalGain]})], ignore_index=True)

            print('for ', i, ' LGain is: ',LTotalGain)
            print('for ', i, ' SGain is: ', STotalGain)
            print(' ')
    else:
        # Iterate through rows within the specified time range, and call strategies
        for index, row in df.loc[begin_datetime:end_datetime].iterrows():
            var = LSimpleStrategy1(False, index, 1, bars1, bars5, bars15)
            var = SSimpleStrategy1(False, index, 1, bars1, bars5, bars15)


