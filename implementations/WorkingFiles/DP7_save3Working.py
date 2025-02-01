from DP_API_IN import Get_Historical_Min, Get_Historical_Day, Get_Syncronous_Real_Time
from DP_GUI import Chart_Plot
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, EquityTrade
from typing import List, Dict
import time
import threading
import pandas as pd
import pandas_ta as ta
from DPStrategies import Run_DP_Strategies

global df1min


# (4Bi) parallel process B - asynchronous websocket real-time data setup
def run_websocket_client():
    #client = WebSocketClient("2zmoradDxePltuU6j2StuFzNo38dmVyD") # hardcoded api_key is used
    client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # hardcoded api_key is used
    client.subscribe("AM.NVDA")  # single ticker
    #client.subscribe("A.*")  # all trades
    client.run(handle_msg)

# (4Bii) parallel process B - synchronous websocket real-time data handler
def handle_msg(msgs: List[WebSocketMessage]):
    aggs = []

    for m in msgs:
        # print(m)

        if m.event_type == 'AM':  # per sec msgs
            aggs.append(m)
            dfRT = pd.DataFrame(aggs,
                                columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'end_timestamp'])

            dfRT['timestamp'] = dfRT['end_timestamp']
            dfRT = dfRT.drop(columns=['end_timestamp'])
            #dfRT['datetime'] = pd.to_datetime(dfRT['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            #dfRT.set_index("datetime", inplace=True)  # index with date time as index axis

            SymbolDataH, df1H = Get_Historical_Min('NVDA', Num_Days_Data) # refresh historical df1min

            merged_df = pd.concat([df1H, dfRT], axis=0)
            df1H = merged_df  # update to merged data, but less datetime index

            merged_df['datetime'] = pd.to_datetime(merged_df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            merged_df.set_index("datetime", inplace=True)  # index with date time as index axis
            #print('Merged print')
            #print(merged_df)

            df = merged_df
            df = df.resample('1T').ffill()

            # resample and set up 5 min bars
            df5 = merged_df.resample("5min").agg({
                "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                "volume": "sum", "timestamp": "last"})
            #print(df5)

            # resample and set up 15 min bars
            df15 = merged_df.resample("15min").agg({
                "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                "volume": "sum", "timestamp": "last"})
            #print(df15)

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

            dfD = Get_Historical_Day('NVDA', 20)
            #print('dfD = ', dfD)
            dfD['datetime'] = pd.to_datetime(dfD['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            dfD.set_index("datetime", inplace=True)  # index with date time as index axis

            #print(df)
            #print( 'SL_SMA14_1M = ',df.iloc[-1]['Sl_SMA14_1M'] )
            #print('SL_SMA50_1M = ', df.iloc[-1]['Sl_SMA50_1M'])

            if True:
                Chart_Plot('NVDA', df, df5, df15, dfD)


# (5) GUI Update
def background_GUI_function():
    #print('GUI Update - Close:', df1min.iloc[-1]['close_1M'] )
    #print(df1min.iloc[-1]['close_1M'])
    print('GUI')



# (4A) parallel process A - update GUI
def run_function_periodically():
    while True:
        background_GUI_function()
        time.sleep(10)                   # 1 sec async rate spec


#*********************************************
# init main app/program begin pre-conditions
#*********************************************
n = 0   #GUI counter parameter init
# (1) Preload Historical Data
Num_Days_Data = 3
SymbolDataH, df1H = Get_Historical_Min('NVDA', Num_Days_Data)



# (2i) initialize main DataFrames for Historical Data
df1min = df1H

#print(df1min)

# (2ii) process historical Data through Strategies
#Run_DP_Strategies(df1min, df5min, df15min, df1day)


# (3) Set up Multi Threads to implement parallel processing (3 channels [this, thd1, thd2])
# and enable Real-Time DataFrames Processing
thread1 = threading.Thread(target=run_function_periodically)
thread2 = threading.Thread(target=run_websocket_client)    # Real-Time begin
thread1.start()
thread2.start()
thread1.join()
thread2.join()

# (2iii) Add Real-Time messages to queue, get indicators, and rn strategies
