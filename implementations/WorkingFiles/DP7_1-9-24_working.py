from DP_API_IN import Get_Historical_Min, Get_Historical_Day
from DP_GUI import Chart_Plot_Std, Chart_Plot_HistoAnalysis, DebugPrints, Chart_Plot_Update
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, EquityTrade
from typing import List, Dict
import time
from datetime import datetime
import threading
import pandas as pd
import pandas_ta as ta
from DP_Indicators import Expand_1minute_Data, StockData
from DP_Strategies import LSimpleStrategy1, SSimpleStrategy1
import winsound
from Backtesting import process_bars
from globals import (PlotOutputStd, PlotOutputHA, BackTest, LiveTradeActive,
     HistBeginDateTime, HistEndDateTime)


#**************************************************************************************
# (4Bi) parallel process B - asynchronous websocket real-time data setup
def run_websocket_client():
    #client = WebSocketClient("2zmoradDxePltuU6j2StuFzNo38dmVyD") # hardcoded api_key is used
    client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # hardcoded api_key is used
    client.subscribe("AM.NVDA")  # single ticker Aggregate
    #client.subscribe("A.*")  # all trades
    client.run(handle_msg)

# (4Bii) parallel process B - synchronous websocket real-time data handler
def handle_msg(msgs: List[WebSocketMessage]):
    aggs = []
    #global df, dfRT, merged_df  #, in_long, in_short

    for m in msgs:
        # print(m)

        if m.event_type == 'AM':  # per unit time selection msgs
            aggs.append(m)
            dfRT = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'end_timestamp'])
            dfRT['timestamp'] = dfRT['end_timestamp']
            dfRT = dfRT.drop(columns=['end_timestamp'])
            SymbolDataH, df1H = Get_Historical_Min('NVDA', Num_Days_Data) # refresh historical df1min
            merged_df = pd.concat([df1H, dfRT], axis=0)
            df1H = merged_df  # update to merged data, but less datetime index
            merged_df['datetime'] = pd.to_datetime(merged_df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            merged_df.set_index("datetime", inplace=True)  # index with date time as index axis
            df = merged_df
            df = df.resample('1T').ffill()
            #print('Before: ', df.iloc[-1].close)
            df, df5, df15 = Expand_1minute_Data(df)    #expand one min to 5 and 15 min, and add typicl indicators to df(s)
                                                        # classes will be used to pass data around mostly
            stock_data_1.load_data(df)   #update class with latest stock data values
            stock_data_5.load_data(df5)  # update class with latest stock data values
            stock_data_15.load_data(df15)  # update class with latest stock data values
            dfD = Get_Historical_Day('NVDA', 30)    # Day data next
            dfD['SMA3_1D'] = ta.sma(dfD['close'], length=3)
            #print('dfD = ', dfD)
            dfD['datetime'] = pd.to_datetime(dfD['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            dfD.set_index("datetime", inplace=True)  # index with date time as index axis

            if PlotOutputStd:
                Chart_Plot_Std('NVDA', df, df5, df15, dfD)

            if LiveTradeActive:
                pass
                #in_long = LSimpleStrategy1(TradeActive, in_long, in_short, stock_data_1, stock_data_5, stock_data_15)
                #in_short = SSimpleStrategy1(TradeActive, in_long, in_short, stock_data_1, stock_data_5, stock_data_15)


# (5) GUI Update
def background_GUI_function():
    #if PlotOutputStd:
    #    Chart_Plot_Std('NVDA', df, df5, df15, dfD)
    if PlotOutputHA:
        Chart_Plot_Update('NVDA', HistBeginDateTime, HistEndDateTime, df, df5, df15, dfD)
    #DebugPrints

# (4A) parallel process A - update GUI
def run_function_periodically():
    while True:
        background_GUI_function()
        #update_plot()
        time.sleep(30)                   # 1 sec async rate spec

#*********************************************
#              MAIN  BEGIN
#*********************************************
# init main app/program pre-conditions
#*********************************************
n = 0   #GUI counter parameter init
# (1) Preload Historical Data and init all DataFrames
begin_datetime = datetime.strptime(HistBeginDateTime, '%Y-%m-%d %H:%M:%S')
end_datetime = datetime.strptime(HistEndDateTime, '%Y-%m-%d %H:%M:%S')
# Calculate the difference in days
days_difference = (end_datetime - begin_datetime).days
Num_Days_Data = days_difference + 3
SymbolDataH, df1H = Get_Historical_Min('NVDA', Num_Days_Data)   #Get historical into a DataFrame
df1H['datetime'] = pd.to_datetime(df1H['timestamp'], unit='ms') - pd.Timedelta(hours=7)
df1H.set_index("datetime", inplace=True)  # index with date time as index axis
df1min = df1H
df, df5, df15 = Expand_1minute_Data(df1H)

#in_long = False
#in_short = False

stock_data_1 = StockData()    #instantiate 1 min bars class to encapsulate data and indicator methods
stock_data_1.load_data(df1H)  #initialize stock_data class with historical data asap
stock_data_5 = StockData()    #instantiate 5 min bars class to encapsulate data and indicator methods
stock_data_5.load_data(df5)  #initialize stock_data class with historical data asap
stock_data_15 = StockData()    #instantiate 15 min bars class to encapsulate data and indicator methods
stock_data_15.load_data(df15)  #initialize stock_data class with historical data asap

dfD = Get_Historical_Day('NVDA', 20)
dfD['SMA3_1D'] = ta.sma(dfD['close'], length=3)
dfD['datetime'] = pd.to_datetime(dfD['timestamp'], unit='ms') - pd.Timedelta(hours=7)
dfD.set_index("datetime", inplace=True)  # index with date time as index axis

#Plot first Historical chart/plot. Others may follow from web socket message handler
if PlotOutputStd:
    Chart_Plot_Std('NVDA', df, df5, df15, dfD)
elif PlotOutputHA:
    Chart_Plot_HistoAnalysis('NVDA', HistBeginDateTime, HistEndDateTime, df, df5, df15, dfD)


#**********
if BackTest:    #this will scan through historical bars, execute strategies, and allor optimization as needed
    process_bars(HistBeginDateTime, HistEndDateTime, df, df5, df15)
    pass
#**********


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

