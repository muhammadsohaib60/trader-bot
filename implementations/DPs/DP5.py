# This program reads Polygon API for historical quotes first, then web sockets, and populates historical and
# real-time quotes in a 1 minute, 5 minute, 15 minute bars timeframe. It gets std API symbol data plus sma (3,14,50,200)
# and Bollinger Bands and populates 3 dataframes for the 3 bars timeframes.

from polygon import RESTClient
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List

pd.options.display.width = 0
pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 100)

# First get historical Data and parse

client = RESTClient("YOUR_API_KEY")         # DEV ENV KEY
#client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")   # TEST ENV KEY

aggs = []

# Get the current date
current_date = datetime.now().date()
# Format the date as YYYY-MM-DD
formatted_date = current_date.strftime("%Y-%m-%d")
print("Indicators Calculating based on Historical's from Current Date (YYYY-MM-DD) and Start Time:", formatted_date)
# Calculate the day prior to the current date
previous_date = current_date - timedelta(days=2)
# Format the previous date as YYYY-MM-DD
formatted_previous_date = previous_date.strftime("%Y-%m-%d")

for a in client.list_aggs(
    "NVDA",
    1,
    "minute",
    #"2023-12-21",    # YYYY-MM-DD  (from)
    #"2023-12-21",    # YYYY-MM-DD  (to)
    formatted_previous_date,    # from date
    formatted_date,             # to date
    limit=50000,
    ):
    aggs.append(a)
#print(aggs)

global df

df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
df.sort_values(by='timestamp', inplace = True)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
df.set_index("datetime", inplace=True)      #index with date time as index axis
df = df.resample('1T').ffill()
#print(df)

# Next Get Streaming Real-Time Data and parse

client = WebSocketClient("YOUR_API_KEY")  # DEV ENV KEY
#client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY
# aggregates (per minute)
# client.subscribe("AM.*") # all aggregates
client.subscribe("AM.NVDA") # single ticker

# aggregates (per second)
# client.subscribe("A.*")  # all aggregates
# client.subscribe("A.NRXP") # single ticker


while True:     # now handle websocket for continuous real-time messages (break out to exit)
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
                df = pd.concat([df, dfRT])
                #print(df)

                # resample and set up 5 min bars
                df5 = df.resample("5min").agg({
                    "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                    "volume": "sum", "timestamp": "last"})
                #print(df5)

                # resample and set up 15 min bars
                df15 = df.resample("15min").agg({
                    "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
                    "volume": "sum", "timestamp": "last"})
                #print(df15)

                df['SMA3_1M'] = ta.sma(df['close'], length=3).astype(float).round(3)
                df['Sl_SMA3_1M'] = ta.slope(ta.sma(df['close'], length=3), length=1).astype(float).round(3)
                df['SMA14_1M'] = ta.sma(df['close'], length=14).astype(float).round(3)
                df['Sl_SMA14_1M'] = ta.slope(ta.sma(df['close'], length=14), length=1).astype(float).round(3)
                df['SMA50_1M'] = ta.sma(df['close'], length=50).astype(float).round(3)
                df['Sl_SMA50_1M'] = ta.slope(ta.sma(df['close'], length=50), length=1).astype(float).round(3)
                df['SMA200_1M'] = ta.sma(df['close'], length=200).astype(float).round(3)
                df['Sl_SMA200_1M'] = ta.slope(ta.sma(df['close'], length=200), length=1).astype(float).round(3)
                #print(df)
                df5['SMA3_5M'] = ta.sma(df5['close'], length=3).astype(float).round(3)
                df5['Sl_SMA3_5M'] = ta.slope(ta.sma(df5['close'], length=3), length=1).astype(float).round(3)
                df5['SMA14_5M'] = ta.sma(df5['close'], length=14).astype(float).round(3)
                df5['Sl_SMA14_5M'] = ta.slope(ta.sma(df5['close'], length=14), length=1).astype(float).round(3)
                df5['SMA50_5M'] = ta.sma(df5['close'], length=50).astype(float).round(3)
                df5['Sl_SMA50_5M'] = ta.slope(ta.sma(df5['close'], length=50), length=1).astype(float).round(3)
                df5['SMA200_5M'] = ta.sma(df5['close'], length=200).astype(float).round(3)
                df5['Sl_SMA200_5M'] = ta.slope(ta.sma(df5['close'], length=200), length=1).astype(float).round(3)
                #print(df5)
                df15['SMA3_15M'] = ta.sma(df15['close'], length=3).astype(float).round(3)
                df15['Sl_SMA3_15M'] = ta.slope(ta.sma(df15['close'], length=3), length=1).astype(float).round(3)
                df15['SMA14_15M'] = ta.sma(df15['close'], length=14).astype(float).round(3)
                df15['Sl_SMA14_15M'] = ta.slope(ta.sma(df15['close'], length=14), length=1).astype(float).round(3)
                df15['SMA50_15M'] = ta.sma(df15['close'], length=50).astype(float).round(3)
                df15['Sl_SMA50_15M'] = ta.slope(ta.sma(df15['close'], length=50), length=1).astype(float).round(3)
                df15['SMA200_15M'] = ta.sma(df15['close'], length=200).astype(float).round(3)
                df15['Sl_SMA200_15M'] = ta.slope(ta.sma(df15['close'], length=200), length=1).astype(float).round(3)
                #print(df15)


                bb = ta.bbands(df['close'], length=14, std=2).astype(float).round(3)
                df = pd.concat([df, bb], axis=1)
                df = df.rename(columns={'BBL_14_2.0': 'BBL1_14_2'})
                df = df.rename(columns={'BBM_14_2.0': 'BBM1_14_2'})
                df = df.rename(columns={'BBU_14_2.0': 'BBU1_14_2'})
                df = df.rename(columns={'BBB_14_2.0': 'BBB1_14_2'})
                df = df.rename(columns={'BBP_14_2.0': 'BBP1_14_2'})
                bb5 = ta.bbands(df5['close'], length=14, std=2).astype(float).round(3)
                df5 = pd.concat([df5, bb5], axis=1)
                df5 = df5.rename(columns={'BBL_14_2.0': 'BBL5_14_2'})
                df5 = df5.rename(columns={'BBM_14_2.0': 'BBM5_14_2'})
                df5 = df5.rename(columns={'BBU_14_2.0': 'BBU5_14_2'})
                df5 = df5.rename(columns={'BBB_14_2.0': 'BBB5_14_2'})
                df5 = df5.rename(columns={'BBP_14_2.0': 'BBP5_14_2'})
                bb15 = ta.bbands(df15['close'], length=14, std=2).astype(float).round(3)
                df15 = pd.concat([df15, bb15], axis=1)
                df15 = df15.rename(columns={'BBL_14_2.0': 'BBL15_14_2'})
                df15 = df15.rename(columns={'BBM_14_2.0': 'BBM15_14_2'})
                df15 = df15.rename(columns={'BBU_14_2.0': 'BBU15_14_2'})
                df15 = df15.rename(columns={'BBB_14_2.0': 'BBB15_14_2'})
                df15 = df15.rename(columns={'BBP_14_2.0': 'BBP15_14_2'})

                print(df)

    client.run(handle_msg)

