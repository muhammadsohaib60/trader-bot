# This program reads Polygon API for historical quotes first, then web sockets, and populates historical and
# real-time quotes in a 1 minute, 5 minute, 15 minute bars timeframe. It gets std API symbol data plus sma (3,14,50,200)
# and Bollinger Bands and populates 3 dataframes for the 3 bars timeframes.

from polygon import RESTClient
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List

pd.options.display.width = 0
pd.set_option('display.max_rows', 12000)
pd.set_option('display.min_rows', 6000)


def Get_Historical(Num_Days_Data):
    # First get historical Data and parse
    client = RESTClient("2zmoradDxePltuU6j2StuFzNo38dmVyD")         # DEV ENV KEY
    #client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")   # TEST ENV KEY

    aggs = []

    # Get the current date
    current_date = datetime.now().date()- timedelta(days=0)
    #current_time = int( round( time.time() * 1000 ))
    #Format the date as YYYY-MM-DD
    formatted_date = current_date.strftime("%Y-%m-%d")
    print("Waiting for 1 minute data message(s)")
    # Calculate 2 day prior to the current date
    previous_date = current_date - timedelta(days=Num_Days_Data)
    #previous_time = current_time - 172800000
    # Format the previous date as YYYY-MM-DD
    formatted_previous_date = previous_date.strftime("%Y-%m-%d")

    # ***************
    # Get 1 day bars
    # ***************
    for a in client.list_aggs(
        "NVDA",
        1,
        "day",
        formatted_previous_date,    # from date
        formatted_date,             # to date
        limit=5000,
        ):
        aggs.append(a)
    #print(aggs)

    global dfd
    global df

    dfd = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
    dfd.sort_values(by='timestamp', inplace = True)
    dfd['datetime'] = pd.to_datetime(dfd['timestamp'], unit='ms') - pd.Timedelta(hours=7)
    dfd.set_index("datetime", inplace=True)      #index with date time as index axis

    dfd['SMA3_1D'] = ta.sma(dfd['close'], length=3)
    dfd['Sl_SMA3_1D'] = ta.slope(ta.sma(dfd['close'], length=3), length=1)

    dfd = dfd.rename(columns={'open': 'open_D'})
    dfd = dfd.rename(columns={'high': 'high_D'})
    dfd = dfd.rename(columns={'low': 'low_D'})
    dfd = dfd.rename(columns={'close': 'close_D'})
    dfd = dfd.rename(columns={'vwap': 'vwap_D'})
    dfd = dfd.rename(columns={'volume': 'volume_D'})
    dfd = dfd.rename(columns={'timestamp': 'timestamp_D'})
    #print(dfd)


    # ***************
    # Get 1 min bars
    # ***************
    for a in client.list_aggs(
        "NVDA",
        1,
        "minute",
        formatted_previous_date,    # from date
        formatted_date,             # to date
        limit=50000,
        ):
        aggs.append(a)
    #print(aggs)


    df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
    df.sort_values(by='timestamp', inplace = True)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
    df.set_index("datetime", inplace=True)      #index with date time as index axis

    dftemp = df
    dftemp = dftemp.resample('1T').ffill()
    dftemp['volume'] =  0
    dftemp['volume'] = df['volume']
    dftemp['volume'] = dftemp['volume'].fillna(0)
    df = dftemp
    #print(dftemp)

    # resample and set up 5 min bars
    df5 = df.resample("5min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df5)

    # resample and set up 15 min bars
    df15 = df.resample("15min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df15)

    df['SMA3_1M'] = ta.sma(df['close'], length=3)
    df['Sl_SMA3_1M'] = ta.slope(ta.sma(df['close'], length=3), length=1)
    df['SMA14_1M'] = ta.sma(df['close'], length=14)
    df['Sl_SMA14_1M'] = ta.slope(ta.sma(df['close'], length=14), length=1)
    df['SMA50_1M'] = ta.sma(df['close'], length=50)
    df['Sl_SMA50_1M'] = ta.slope(ta.sma(df['close'], length=50), length=1)
    df['SMA200_1M'] = ta.sma(df['close'], length=200)
    df['Sl_SMA200_1M'] = ta.slope(ta.sma(df['close'], length=200), length=1)
    # print(df)

    df5['SMA3_5M'] = ta.sma(df5['close'], length=3)
    df5['Sl_SMA3_5M'] = ta.slope(ta.sma(df5['close'], length=3), length=1)
    df5['SMA14_5M'] = ta.sma(df5['close'], length=14)
    df5['Sl_SMA14_5M'] = ta.slope(ta.sma(df5['close'], length=14), length=1)
    df5['SMA50_5M'] = ta.sma(df5['close'], length=50)
    df5['Sl_SMA50_5M'] = ta.slope(ta.sma(df5['close'], length=50), length=1)
    df5['SMA200_5M'] = ta.sma(df5['close'], length=200)
    df5['Sl_SMA200_5M'] = ta.slope(ta.sma(df5['close'], length=200), length=1)
    #print(df5)

    df15['SMA3_15M'] = ta.sma(df15['close'], length=3)
    df15['Sl_SMA3_15M'] = ta.slope(ta.sma(df15['close'], length=3), length=1)
    df15['SMA14_15M'] = ta.sma(df15['close'], length=14)
    df15['Sl_SMA14_15M'] = ta.slope(ta.sma(df15['close'], length=14), length=1)
    df15['SMA50_15M'] = ta.sma(df15['close'], length=50)
    df15['Sl_SMA50_15M'] = ta.slope(ta.sma(df15['close'], length=50), length=1)
    df15['SMA200_15M'] = ta.sma(df15['close'], length=200)
    df15['Sl_SMA200_15M'] = ta.slope(ta.sma(df15['close'], length=200), length=1)
    #print(df15)

    bb = ta.bbands(df['close'], length=14, std=2)
    df = pd.concat([df, bb], axis=1)
    df = df.rename(columns={'BBL_14_2.0': 'BBL1_14_2'})
    df = df.rename(columns={'BBM_14_2.0': 'BBM1_14_2'})
    df = df.rename(columns={'BBU_14_2.0': 'BBU1_14_2'})
    df = df.rename(columns={'BBB_14_2.0': 'BBB1_14_2'})
    df = df.rename(columns={'BBP_14_2.0': 'BBP1_14_2'})
    bb5 = ta.bbands(df5['close'], length=14, std=2)
    df5 = pd.concat([df5, bb5], axis=1)
    df5 = df5.rename(columns={'BBL_14_2.0': 'BBL5_14_2'})
    df5 = df5.rename(columns={'BBM_14_2.0': 'BBM5_14_2'})
    df5 = df5.rename(columns={'BBU_14_2.0': 'BBU5_14_2'})
    df5 = df5.rename(columns={'BBB_14_2.0': 'BBB5_14_2'})
    df5 = df5.rename(columns={'BBP_14_2.0': 'BBP5_14_2'})
    bb15 = ta.bbands(df15['close'], length=14, std=2)
    df15 = pd.concat([df15, bb15], axis=1)
    df15 = df15.rename(columns={'BBL_14_2.0': 'BBL15_14_2'})
    df15 = df15.rename(columns={'BBM_14_2.0': 'BBM15_14_2'})
    df15 = df15.rename(columns={'BBU_14_2.0': 'BBU15_14_2'})
    df15 = df15.rename(columns={'BBB_14_2.0': 'BBB15_14_2'})
    df15 = df15.rename(columns={'BBP_14_2.0': 'BBP15_14_2'})

    df = df.rename(columns={'open': 'open_1M'})
    df = df.rename(columns={'high': 'high_1M'})
    df = df.rename(columns={'low': 'low_1M'})
    df = df.rename(columns={'close': 'close_1M'})
    df = df.rename(columns={'vwap': 'vwap_1M'})
    df = df.rename(columns={'volume': 'volume_1M'})
    df = df.rename(columns={'timestamp': 'timestamp_1M'})
    df5 = df5.rename(columns={'open': 'open_5M'})
    df5 = df5.rename(columns={'high': 'high_5M'})
    df5 = df5.rename(columns={'low': 'low_5M'})
    df5 = df5.rename(columns={'close': 'close_5M'})
    df5 = df5.rename(columns={'vwap': 'vwap_5M'})
    df5 = df5.rename(columns={'volume': 'volume_5M'})
    df5 = df5.rename(columns={'timestamp': 'timestamp_5M'})
    df15 = df15.rename(columns={'open': 'open_15M'})
    df15 = df15.rename(columns={'high': 'high_15M'})
    df15 = df15.rename(columns={'low': 'low_15M'})
    df15 = df15.rename(columns={'close': 'close_15M'})
    df15 = df15.rename(columns={'vwap': 'vwap_15M'})
    df15 = df15.rename(columns={'volume': 'volume_15M'})
    df15 = df15.rename(columns={'timestamp': 'timestamp_15M'})

    #print(df)
    return df, df5, df15, dfd


def Get_HistReal(Num_Days_Data):

    # First get historical Data and parse
    client = RESTClient("2zmoradDxePltuU6j2StuFzNo38dmVyD")  # DEV ENV KEY
    # client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")   # TEST ENV KEY

    aggs = []

    # Get the current date
    current_date = datetime.now().date() - timedelta(days=0)
    # current_time = int( round( time.time() * 1000 ))
    # Format the date as YYYY-MM-DD
    formatted_date = current_date.strftime("%Y-%m-%d")
    print("Waiting for 1 minute data message(s)")
    # Calculate 2 day prior to the current date
    previous_date = current_date - timedelta(days=Num_Days_Data)
    # previous_time = current_time - 172800000
    # Format the previous date as YYYY-MM-DD
    formatted_previous_date = previous_date.strftime("%Y-%m-%d")

    for a in client.list_aggs(
            "NVDA",
            1,
            "minute",
            formatted_previous_date,  # from date
            formatted_date,  # to date
            limit=50000,
    ):
        aggs.append(a)
    # print(aggs)

    global df

    df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
    df.sort_values(by='timestamp', inplace=True)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
    df.set_index("datetime", inplace=True)  # index with date time as index axis

    dftemp = df
    dftemp = dftemp.resample('1T').ffill()
    dftemp['volume'] = 0
    dftemp['volume'] = df['volume']
    dftemp['volume'] = dftemp['volume'].fillna(0)
    df = dftemp
    # print(dftemp)

    # resample and set up 5 min bars
    df5 = df.resample("5min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df5)

    # resample and set up 15 min bars
    df15 = df.resample("15min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df15)

    df['SMA3_1M'] = ta.sma(df['close'], length=3)
    df['Sl_SMA3_1M'] = ta.slope(ta.sma(df['close'], length=3), length=1)
    df['SMA14_1M'] = ta.sma(df['close'], length=14)
    df['Sl_SMA14_1M'] = ta.slope(ta.sma(df['close'], length=14), length=1)
    df['SMA50_1M'] = ta.sma(df['close'], length=50)
    df['Sl_SMA50_1M'] = ta.slope(ta.sma(df['close'], length=50), length=1)
    df['SMA200_1M'] = ta.sma(df['close'], length=200)
    df['Sl_SMA200_1M'] = ta.slope(ta.sma(df['close'], length=200), length=1)
    # print(df)

    df5['SMA3_5M'] = ta.sma(df5['close'], length=3)
    df5['Sl_SMA3_5M'] = ta.slope(ta.sma(df5['close'], length=3), length=1)
    df5['SMA14_5M'] = ta.sma(df5['close'], length=14)
    df5['Sl_SMA14_5M'] = ta.slope(ta.sma(df5['close'], length=14), length=1)
    df5['SMA50_5M'] = ta.sma(df5['close'], length=50)
    df5['Sl_SMA50_5M'] = ta.slope(ta.sma(df5['close'], length=50), length=1)
    df5['SMA200_5M'] = ta.sma(df5['close'], length=200)
    df5['Sl_SMA200_5M'] = ta.slope(ta.sma(df5['close'], length=200), length=1)
    # print(df5)

    df15['SMA3_15M'] = ta.sma(df15['close'], length=3)
    df15['Sl_SMA3_15M'] = ta.slope(ta.sma(df15['close'], length=3), length=1)
    df15['SMA14_15M'] = ta.sma(df15['close'], length=14)
    df15['Sl_SMA14_15M'] = ta.slope(ta.sma(df15['close'], length=14), length=1)
    df15['SMA50_15M'] = ta.sma(df15['close'], length=50)
    df15['Sl_SMA50_15M'] = ta.slope(ta.sma(df15['close'], length=50), length=1)
    df15['SMA200_15M'] = ta.sma(df15['close'], length=200)
    df15['Sl_SMA200_15M'] = ta.slope(ta.sma(df15['close'], length=200), length=1)
    # print(df15)

    bb = ta.bbands(df['close'], length=14, std=2)
    df = pd.concat([df, bb], axis=1)
    df = df.rename(columns={'BBL_14_2.0': 'BBL_14_2_1M'})
    df = df.rename(columns={'BBM_14_2.0': 'BBM_14_2_1M'})
    df = df.rename(columns={'BBU_14_2.0': 'BBU_14_2_1M'})
    df = df.rename(columns={'BBB_14_2.0': 'BBB_14_2_1M'})
    df = df.rename(columns={'BBP_14_2.0': 'BBP_14_2_1M'})
    bb5 = ta.bbands(df5['close'], length=14, std=2)
    df5 = pd.concat([df5, bb5], axis=1)
    df5 = df5.rename(columns={'BBL_14_2.0': 'BBL_14_2_5M'})
    df5 = df5.rename(columns={'BBM_14_2.0': 'BBM_14_2_5M'})
    df5 = df5.rename(columns={'BBU_14_2.0': 'BBU_14_2_5M'})
    df5 = df5.rename(columns={'BBB_14_2.0': 'BBB_14_2_5M'})
    df5 = df5.rename(columns={'BBP_14_2.0': 'BBP_14_2_5M'})
    bb15 = ta.bbands(df15['close'], length=14, std=2)
    df15 = pd.concat([df15, bb15], axis=1)
    df15 = df15.rename(columns={'BBL_14_2.0': 'BBL15_14_2_15M'})
    df15 = df15.rename(columns={'BBM_14_2.0': 'BBM15_14_2_15M'})
    df15 = df15.rename(columns={'BBU_14_2.0': 'BBU15_14_2_15M'})
    df15 = df15.rename(columns={'BBB_14_2.0': 'BBB15_14_2_15M'})
    df15 = df15.rename(columns={'BBP_14_2.0': 'BBP15_14_2_15M'})

    df = df.rename(columns={'open': 'open_1M'})
    df = df.rename(columns={'high': 'high_1M'})
    df = df.rename(columns={'low': 'low_1M'})
    df = df.rename(columns={'close': 'close_1M'})
    df = df.rename(columns={'vwap': 'vwap_1M'})
    df = df.rename(columns={'volume': 'volume_1M'})
    df = df.rename(columns={'timestamp': 'timestamp_1M'})
    df5 = df5.rename(columns={'open': 'open_5M'})
    df5 = df5.rename(columns={'high': 'high_5M'})
    df5 = df5.rename(columns={'low': 'low_5M'})
    df5 = df5.rename(columns={'close': 'close_5M'})
    df5 = df5.rename(columns={'vwap': 'vwap_5M'})
    df5 = df5.rename(columns={'volume': 'volume_5M'})
    df5 = df5.rename(columns={'timestamp': 'timestamp_5M'})
    df15 = df15.rename(columns={'open': 'open_15M'})
    df15 = df15.rename(columns={'high': 'high_15M'})
    df15 = df15.rename(columns={'low': 'low_15M'})
    df15 = df15.rename(columns={'close': 'close_15M'})
    df15 = df15.rename(columns={'vwap': 'vwap_15M'})
    df15 = df15.rename(columns={'volume': 'volume_15M'})
    df15 = df15.rename(columns={'timestamp': 'timestamp_15M'})

    # print(df)
    return df, df5, df15, dfd

    # ****************************************************************************************
    # Next Get Streaming Real-Time Data
    # ****************************************************************************************
    client = WebSocketClient("2zmoradDxePltuU6j2StuFzNo38dmVyD")  # DEV ENV KEY
    #client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY
    # aggregates (per minute)
    # client.subscribe("AM.*") # all aggregates
    client.subscribe("AM.NVDA") # single ticker

    # aggregates (per second)
    # client.subscribe("A.*")  # all aggregates
    # client.subscribe("A.NRXP") # single ticker

    def handle_msg(msgs: List[WebSocketMessage]):  # message handler function for clients as subscribed
        # Init
        global df
        aggs = []

        for m in msgs:
            #print(m)

            if m.event_type == 'AM':  # per minute msgs
                aggs.append(m)
                dfRT = pd.DataFrame(aggs,
                                      columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'end_timestamp'])

                dfRT['timestamp'] = dfRT['end_timestamp']
                dfRT= dfRT.drop(columns=['end_timestamp'])
                dfRT['datetime'] = pd.to_datetime(dfRT['timestamp'], unit='ms') - pd.Timedelta(hours=7)
                dfRT.set_index("datetime", inplace=True)  # index with date time as index axis
                #print(dfRT)
                #print(df)
                #df = df.resample('1T').ffill()
                #df = pd.concat([df, dfRT])
                #df = df.append(dfRT.iloc[-1], ignore_index=True)
                df = pd.concat([df, dfRT.iloc[-1].to_frame().T])
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
                df.set_index("datetime", inplace=True)  # index with date time as index axis
                df = df.resample('1T').ffill(limit=30)
                #print(df)

                dftemp = df
                dftemp = dftemp.resample('1T').ffill()
                dftemp['volume'] = 0
                dftemp['volume'] = df['volume']
                dftemp['volume'] = dftemp['volume'].fillna(0)
                df = dftemp
                # print(dftemp)

                # resample and set up 5 min bars
                df5 = df.resample("5min").agg({
                    "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                    "volume": "sum", "timestamp": "last"})
                # print(df5)

                # resample and set up 15 min bars
                df15 = df.resample("15min").agg({
                    "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                    "volume": "sum", "timestamp": "last"})
                # print(df15)

                df['SMA3_1M'] = ta.sma(df['close'], length=3)
                df['Sl_SMA3_1M'] = ta.slope(ta.sma(df['close'], length=3), length=1)
                df['SMA14_1M'] = ta.sma(df['close'], length=14)
                df['Sl_SMA14_1M'] = ta.slope(ta.sma(df['close'], length=14), length=1)
                df['SMA50_1M'] = ta.sma(df['close'], length=50)
                df['Sl_SMA50_1M'] = ta.slope(ta.sma(df['close'], length=50), length=1)
                df['SMA200_1M'] = ta.sma(df['close'], length=200)
                df['Sl_SMA200_1M'] = ta.slope(ta.sma(df['close'], length=200), length=1)
                # print(df)

                df5['SMA3_5M'] = ta.sma(df5['close'], length=3)
                df5['Sl_SMA3_5M'] = ta.slope(ta.sma(df5['close'], length=3), length=1)
                df5['SMA14_5M'] = ta.sma(df5['close'], length=14)
                df5['Sl_SMA14_5M'] = ta.slope(ta.sma(df5['close'], length=14), length=1)
                df5['SMA50_5M'] = ta.sma(df5['close'], length=50)
                df5['Sl_SMA50_5M'] = ta.slope(ta.sma(df5['close'], length=50), length=1)
                df5['SMA200_5M'] = ta.sma(df5['close'], length=200)
                df5['Sl_SMA200_5M'] = ta.slope(ta.sma(df5['close'], length=200), length=1)
                # print(df5)

                df15['SMA3_15M'] = ta.sma(df15['close'], length=3)
                df15['Sl_SMA3_15M'] = ta.slope(ta.sma(df15['close'], length=3), length=1)
                df15['SMA14_15M'] = ta.sma(df15['close'], length=14)
                df15['Sl_SMA14_15M'] = ta.slope(ta.sma(df15['close'], length=14), length=1)
                df15['SMA50_15M'] = ta.sma(df15['close'], length=50)
                df15['Sl_SMA50_15M'] = ta.slope(ta.sma(df15['close'], length=50), length=1)
                df15['SMA200_15M'] = ta.sma(df15['close'], length=200)
                df15['Sl_SMA200_15M'] = ta.slope(ta.sma(df15['close'], length=200), length=1)
                # print(df15)

                bb = ta.bbands(df['close'], length=14, std=2)
                df = pd.concat([df, bb], axis=1)
                df = df.rename(columns={'BBL_14_2.0': 'BBL1_14_2'})
                df = df.rename(columns={'BBM_14_2.0': 'BBM1_14_2'})
                df = df.rename(columns={'BBU_14_2.0': 'BBU1_14_2'})
                df = df.rename(columns={'BBB_14_2.0': 'BBB1_14_2'})
                df = df.rename(columns={'BBP_14_2.0': 'BBP1_14_2'})
                bb5 = ta.bbands(df5['close'], length=14, std=2)
                df5 = pd.concat([df5, bb5], axis=1)
                df5 = df5.rename(columns={'BBL_14_2.0': 'BBL5_14_2'})
                df5 = df5.rename(columns={'BBM_14_2.0': 'BBM5_14_2'})
                df5 = df5.rename(columns={'BBU_14_2.0': 'BBU5_14_2'})
                df5 = df5.rename(columns={'BBB_14_2.0': 'BBB5_14_2'})
                df5 = df5.rename(columns={'BBP_14_2.0': 'BBP5_14_2'})
                bb15 = ta.bbands(df15['close'], length=14, std=2)
                df15 = pd.concat([df15, bb15], axis=1)
                df15 = df15.rename(columns={'BBL_14_2.0': 'BBL15_14_2'})
                df15 = df15.rename(columns={'BBM_14_2.0': 'BBM15_14_2'})
                df15 = df15.rename(columns={'BBU_14_2.0': 'BBU15_14_2'})
                df15 = df15.rename(columns={'BBB_14_2.0': 'BBB15_14_2'})
                df15 = df15.rename(columns={'BBP_14_2.0': 'BBP15_14_2'})

                df = df.rename(columns={'open': 'open_1M'})
                df = df.rename(columns={'high': 'high_1M'})
                df = df.rename(columns={'low': 'low_1M'})
                df = df.rename(columns={'close': 'close_1M'})
                df = df.rename(columns={'vwap': 'vwap_1M'})
                df = df.rename(columns={'volume': 'volume_1M'})
                df = df.rename(columns={'timestamp': 'timestamp_1M'})
                df5 = df5.rename(columns={'open': 'open_5M'})
                df5 = df5.rename(columns={'high': 'high_5M'})
                df5 = df5.rename(columns={'low': 'low_5M'})
                df5 = df5.rename(columns={'close': 'close_5M'})
                df5 = df5.rename(columns={'vwap': 'vwap_5M'})
                df5 = df5.rename(columns={'volume': 'volume_5M'})
                df5 = df5.rename(columns={'timestamp': 'timestamp_5M'})
                df15 = df15.rename(columns={'open': 'open_15M'})
                df15 = df15.rename(columns={'high': 'high_15M'})
                df15 = df15.rename(columns={'low': 'low_15M'})
                df15 = df15.rename(columns={'close': 'close_15M'})
                df15 = df15.rename(columns={'vwap': 'vwap_15M'})
                df15 = df15.rename(columns={'volume': 'volume_15M'})
                df15 = df15.rename(columns={'timestamp': 'timestamp_15M'})

                # print(df)
                # return df, df5, df15



    client.run(handle_msg)


