from DP_API_IN import Get_Historical, Get_Syncronous_Real_Time
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from DP_GUI import Chart_Plot
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, EquityTrade
from typing import List, Dict
from datetime import datetime
import time
import threading
import pandas as pd
from DPStrategies import Run_DP_Strategies

global df1H, df5H, df15H, dfdH, SymbolDataH, n, df1min, df5min, df15min, df1day

# (4Bi) parallel process B - asynchronous websocket real-time data setup
def run_websocket_client():
    #client = WebSocketClient("YOUR_API_KEY") # hardcoded api_key is used
    client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # hardcoded api_key is used
    client.subscribe("A.*")  # all trades
    client.run(handle_msg)

# (4Bii) parallel process B - synchronous websocket real-time data handler
def handle_msg(msgs: List[WebSocketMessage]):
    aggs = []
    global dfRT

    for m in msgs:
        # print(m)

        if m.event_type == 'A':  # per sec msgs
            aggs.append(m)
            dfRT = pd.DataFrame(aggs,
                                columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'end_timestamp'])

            dfRT['timestamp'] = dfRT['end_timestamp']
            dfRT = dfRT.drop(columns=['end_timestamp'])
            dfRT['datetime'] = pd.to_datetime(dfRT['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            dfRT.set_index("datetime", inplace=True)  # index with date time as index axis
            #print(dfRT)

        #Need to conditionally merge dfRT with df1min !!! if real time trading if/when ready

        # Run strategies on Historical only for now
        Run_DP_Strategies(df1min, df5min, df15min, df1day)


# (5) GUI Update
def background_GUI_function():
    n=n+1
    print('GUI Update - Close:', n, df1min.iloc[-1]['close_1M'] )
    #print(df1min.iloc[-1]['close_1M'])


# (4A) parallel process A - update GUI
def run_function_periodically():
    while True:
        background_GUI_function()
        time.sleep(1)                   # 1 sec async rate spec


#*********************************************
# init main app/program begin pre-conditions
#*********************************************
n = 0   #GUI counter parameter init
# (1) Preload Historical Data
Num_Days_Data = 1
SymbolDataH, df1H, df5H, df15H, dfdH = Get_Historical('NVDA', Num_Days_Data)

# (2i) initialize main DataFrames for Historical Data
df1min = df1H
df5min = df5H
df15min = df15H
df1day = dfdH
# (2ii) process historical Data through Strategies
Run_DP_Strategies(df1min, df5min, df15min, df1day)


# (3) Set up Multi Threads to implement parallel processing (3 channels [this, thd1, thd2])
# and enable Real-Time DataFrames Processing
thread1 = threading.Thread(target=run_function_periodically)
thread2 = threading.Thread(target=run_websocket_client)
thread1.start()
thread2.start()
thread1.join()
thread2.join()

# (2iii) Add Real-Time messages to queue, get indicators, and rn strategies
