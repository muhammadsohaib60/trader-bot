
# This program reads Polygon REST API for historical quotes first,
# then web sockets, and populates historical and
# real-time quotes in a 1 minute, 5 minute, 15 minute bars, and day bars timeframes.
# For each, it populates std API symbol data plus sma (3,14,50,200)
# and Bollinger Bands and populates 3 dataframes for the 4 bars timeframes.

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
from DP_GUI import Chart_Plot

pd.options.display.width = 0
pd.set_option('display.max_rows', 12000)
pd.set_option('display.min_rows', 6000)

# (1) Preload Historical Data - Function
def Get_Historical_Min(Ticker, Num_Days_Data):

    # First get historical Data and parse
    client = RESTClient("YOUR_API_KEY")         # DEV ENV KEY
    #client = RESTClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")        # TEST ENV KEY

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
    # Get 1 min bars
    # ***************
    for a in client.list_aggs(
        Ticker,
        1,
        "minute",
        formatted_previous_date,    # from date
        formatted_date,             # to date
        limit=50000,
        ):
        aggs.append(a)
    #print(aggs)


    df1 = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
    df1.sort_values(by='timestamp', inplace = True)


    #print(df)
    return Ticker, df1

def Get_Historical_Day(Ticker, Num_Days_Data):

    # First get historical Data and parse
    client = RESTClient("YOUR_API_KEY")         # DEV ENV KEY
    #client = RESTClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")        # TEST ENV KEY

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
    # Get 1 min bars
    # ***************
    for a in client.list_aggs(
        Ticker,
        1,
        "day",
        formatted_previous_date,    # from date
        formatted_date,             # to date
        limit=5000,
        ):
        aggs.append(a)
    #print(aggs)


    dfD = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
    dfD.sort_values(by='timestamp', inplace = True)

    #print(dfD)
    return dfD

#*************************************************************************************


def Get_Syncronous_Real_Time(Key, Timeframe, Ticker):
    # This function uses ticker data driven message handler, to provide an event
    # on each occurance of the Ticker, at a nominal Timeframe (sec, min). Data may
    # or may-not occur in this timeframe interval however, so fill is needed for syncronous data
    global dfRT

    if Key == '1':
        client = WebSocketClient("YOUR_API_KEY")  # DEV ENV KEY
    elif Key == '2':
        #client = WebSocketClient("YOUR_API_KEY")
        client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY
    else:
        #client = WebSocketClient("YOUR_API_KEY")
        client = WebSocketClient("TBD")  # NULL ENV KEY

    if Timeframe == 'sec':
        prefix = "A"
    elif Timeframe == 'min':
        prefix = "AM"

    subscriber_string = prefix + '.' + Ticker
    client.subscribe( subscriber_string )

    def handle_msg(msgs: List[WebSocketMessage]):  # message handler function
        aggs = []
        #dfRT_Queue = pd.DataFrame( columns=['symbol', 'event_type', 'open', 'high', 'low', 'close', 'vwap',
        #       'volume', 'end_timestamp', 'accumulated_volume', 'official_open_price', 'average_size'])

        for m in msgs:
            #print(m)
            if m.event_type == prefix:  # per sec or min depending on prefix
                aggs.append(m)
                dfRT = pd.DataFrame(aggs,
                        columns=['symbol', 'event_type', 'open', 'high', 'low', 'close', 'vwap', 'volume',
                                    'end_timestamp', 'accumulated_volume', 'official_open_price',
                                    'average_size'])
                dfRT['timestamp'] = dfRT['end_timestamp']
                #dfRT= dfRT.drop(columns=['end_timestamp'])
                dfRT['datetime'] = pd.to_datetime(dfRT['timestamp'], unit='ms') - pd.Timedelta(hours=7)
                dfRT.set_index("datetime", inplace=True)  # index with date time as index axis
                #print(dfRT)

    client.run(handle_msg)


