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
pd.set_option('display.max_rows', 120)
pd.set_option('display.min_rows', 60)

sec_aggs = []    # init list of seconds timeframe aggregate messages
min_aggs = []    # init list of minutes timeframe aggregate messages

# First get historical Data and parse

client = RESTClient("YOUR_API_KEY")

aggs = []

# Get the current date
current_date = datetime.now().date()
# Format the date as YYYY-MM-DD
formatted_date = current_date.strftime("%Y-%m-%d")
print("Indicators Calculating based on Historical's from Current Date (YYYY-MM-DD) and Start Time:", formatted_date)
# Calculate the day prior to the current date
previous_date = current_date - timedelta(days=1)
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

#df=pd.DataFrame(aggs)
global df
global InLong
global InShort
InLong = 0
InShort = 0

global LEnterPrice
global SEnterPrice
global i
global LongTradeCount
global ShortTradeCount
LEnterPrice = 0
SEnterPrice = 0
LSumGain = 0
SSumGain = 0
SumGain = 0
LongTradeCount = 0
ShortTradeCount = 0
LongProfitableCount = 0
ShortProfitableCount = 0
i = 0

df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'vwap', 'volume', 'timestamp'])
df.sort_values(by='timestamp', inplace = True)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
df.set_index("datetime", inplace=True)      #index with date time as index axis
# df = df.drop(columns=['timestamp'])
# print(df)

# Next Get Streaming Real-Time Data and parse

client = WebSocketClient("YOUR_API_KEY")  # DEV ENV KEY - POLYGON_API_KEY environment variable is used
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
        global InLong
        global InShort
        global LEnterPrice
        global LExitPrice
        global SEnterPrice
        global SExitPrice
        global LGain
        global SGain
        global LSumGain
        global SSumGain
        global i
        global LongTradeCount
        global ShortTradeCount
        global LongProfitableCount
        global ShortProfitableCount

        AlgosRunning = False
        open = 0
        high = 0
        low = 0
        close = 0
        volume = 0
        diff = 0.09
        ProfitDelta = 0.5
        StopLossDelta = 0.15
        LongTradeCount = 0
        ShortTradeCount = 0
        LongProfitableCount = 0
        ShortProfitableCount = 0

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

                # 5 min bars
                df5 = df.resample("5min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum"})
                #print(df5)

                # 15 min bars
                df15 = df.resample("15min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum"})
                #print(df15)

                df['SMA3_1M'] = ta.sma(df['close'], length=3)
                df['Slope_SMA3_1M'] = ta.slope(ta.sma(df['close'], length=3), length=1)
                df['SMA14_1M'] = ta.sma(df['close'], length=14)
                df['Slope_SMA14_1M'] = ta.slope(ta.sma(df['close'], length=14), length=1)
                df['SMA50_1M'] = ta.sma(df['close'], length=50)
                df['Slope_SMA50_1M'] = ta.slope(ta.sma(df['close'], length=50), length=1)
                df['SMA200_1M'] = ta.sma(df['close'], length=200)
                df['Slope_SMA200_1M'] = ta.slope(ta.sma(df['close'], length=200), length=1)
                #print(df)
                df5['SMA3_5M'] = ta.sma(df5['close'], length=3)
                df5['Slope_SMA3_5M'] = ta.slope(ta.sma(df5['close'], length=3), length=1)
                df5['SMA14_5M'] = ta.sma(df5['close'], length=14)
                df5['Slope_SMA14_5M'] = ta.slope(ta.sma(df5['close'], length=14), length=1)
                df5['SMA50_5M'] = ta.sma(df5['close'], length=50)
                df5['Slope_SMA50_5M'] = ta.slope(ta.sma(df5['close'], length=50), length=1)
                df5['SMA200_5M'] = ta.sma(df5['close'], length=200)
                df5['Slope_SMA200_5M'] = ta.slope(ta.sma(df5['close'], length=200), length=1)
                #print(df5)
                df15['SMA3_15M'] = ta.sma(df15['close'], length=3)
                df15['Slope_SMA3_15M'] = ta.slope(ta.sma(df15['close'], length=3), length=1)
                df15['SMA14_15M'] = ta.sma(df15['close'], length=14)
                df15['Slope_SMA14_15M'] = ta.slope(ta.sma(df15['close'], length=14), length=1)
                df15['SMA50_15M'] = ta.sma(df15['close'], length=50)
                df15['Slope_SMA50_15M'] = ta.slope(ta.sma(df15['close'], length=50), length=1)
                df15['SMA200_15M'] = ta.sma(df15['close'], length=200)
                df15['Slope_SMA200_15M'] = ta.slope(ta.sma(df15['close'], length=200), length=1)
                #print(df15)

                ''' 
                #Set up main indicators for use
                IND_1M_SMA3 = ta.sma(df['close'], length=3)
                Slope_1M_SMA3 = ta.slope(ta.sma(df['close'], length=3), length=1)
                IND_5M_SMA3 = ta.sma(df5['close'], length=3)
                Slope_5M_SMA3 = ta.slope(ta.sma(df5['close'], length=3), length=1)
                IND_15M_SMA3 = ta.sma(df15['close'], length=3)
                Slope_15M_SMA3 = ta.slope(ta.sma(df15['close'], length=3), length=1)

                IND_1M_SMA14 = ta.sma(df['close'], length=14)
                Slope_1M_SMA14 = ta.slope(ta.sma(df['close'], length=14), length=1)
                IND_5M_SMA14 = ta.sma(df5['close'], length=14)
                Slope_5M_SMA14 = ta.slope(ta.sma(df5['close'], length=14), length=1)
                IND_15M_SMA14 = ta.sma(df15['close'], length=14)
                Slope_15M_SMA14 = ta.slope(ta.sma(df15['close'], length=14), length=1)

                IND_1M_SMA50 = ta.sma(df['close'], length=50)
                Slope_1M_SMA50 = ta.slope(ta.sma(df['close'], length=50), length=1)
                IND_5M_SMA50 = ta.sma(df5['close'], length=50)
                Slope_5M_SMA50 = ta.slope(ta.sma(df5['close'], length=50), length=1)
                IND_15M_SMA50 = ta.sma(df15['close'], length=50)
                Slope_15M_SMA50 = ta.slope(ta.sma(df15['close'], length=50), length=1)

                IND_1M_SMA200 = ta.sma(df['close'], length=200)
                Slope_1M_SMA200 = ta.slope(ta.sma(df['close'], length=200), length=1)
                IND_5M_SMA200 = ta.sma(df5['close'], length=200)
                Slope_5M_SMA200 = ta.slope(ta.sma(df5['close'], length=200), length=1)
                IND_15M_SMA200 = ta.sma(df15['close'], length=200)
                Slope_15M_SMA200 = ta.slope(ta.sma(df15['close'], length=200), length=1)
                '''


                #print(df)

                if False:
                    print('Close = ',df.close.tail(1).item() )
                    print('IND_1M SMA3 = ',IND_1M_SMA3.tail(1).item())
                    print('SLOPE IND_1M SMA3 = ', Slope_1M_SMA3.tail(1).item())
                    print('IND_5M SMA3 = ', IND_5M_SMA3.tail(1).item())
                    print('SLOPE IND_5M SMA3 = ', Slope_5M_SMA3.tail(1).item())
                    print('IND_15M SMA3 = ', IND_15M_SMA3.tail(1).item())
                    print('SLOPE IND_15M SMA3 = ', Slope_15M_SMA3.tail(1).item())
                    print(' ')
                    print('IND_1M SMA14 = ', IND_1M_SMA14.tail(1).item())
                    print('SLOPE IND_1M SMA14 = ', Slope_1M_SMA14.tail(1).item())
                    print('IND_5M SMA14 = ', IND_5M_SMA14.tail(1).item())
                    print('SLOPE IND_5M SMA14 = ', Slope_5M_SMA14.tail(1).item())
                    print('IND_15M SMA14 = ', IND_15M_SMA14.tail(1).item())
                    print('SLOPE IND_15M SMA14 = ', Slope_15M_SMA14.tail(1).item())
                    print(' ')
                    print('IND_1M SMA50 = ', IND_1M_SMA50.tail(1).item())
                    print('SLOPE IND_1M SMA50 = ', Slope_1M_SMA50.tail(1).item())
                    print('IND_5M SMA50 = ', IND_5M_SMA50.tail(1).item())
                    print('SLOPE IND_5M SMA50 = ', Slope_5M_SMA50.tail(1).item())
                    #print('IND_15M SMA50 = ', IND_15M_SMA50.tail(1).item())
                    #print('SLOPE IND_15M SMA50 = ', Slope_15M_SMA50.tail(1).item())
                    print(' ')
                    print('IND_1M SMA200 = ', IND_1M_SMA200.tail(1).item())
                    print('SLOPE IND_1M SMA200 = ', Slope_1M_SMA200.tail(1).item())
                    #print('IND_5M SMA200 = ', IND_5M_SMA200.tail(1).item())
                    #print('SLOPE IND_5M SMA200 = ', Slope_5M_SMA200.tail(1).item())
                    #print('IND_15M SMA200 = ', IND_15M_SMA200.tail(1).item())
                    #print('SLOPE IND_15M SMA200 = ', Slope_15M_SMA200.tail(1).item())
                    print(' ')


                bb = ta.bbands(df['close'], length=14, std=2).astype(float).round(3)
                df = pd.concat([df, bb], axis=1)
                #bb5 = ta.bbands(df5['close'], length=14, std=2).astype(float).round(3)
                #df5 = pd.concat([df5, bb5], axis=1)
                print(df)

                ''' 
                #print(bb)
                bbl_1M = df['BBL_14_2.0'].tail(1).item()
                bbm_1M = df['BBM_14_2.0'].tail(1).item()
                bbu_1M = df['BBU_14_2.0'].tail(1).item()
                bbb_1M = df['BBB_14_2.0'].tail(1).item()
                bbp_1M = df['BBP_14_2.0'].tail(1).item()

                df = df.drop(columns=['BBL_14_2.0'])
                df = df.drop(columns=['BBM_14_2.0'])
                df = df.drop(columns=['BBU_14_2.0'])
                df = df.drop(columns=['BBB_14_2.0'])
                df = df.drop(columns=['BBP_14_2.0'])

                #print('bbl_1M = ', bbl_1M)
                #print('bbm_1M = ', bbm_1M)
                #print('bbu_1M = ', bbu_1M)
                #print('bbb_1M = ', bbb_1M)
                #print('bbp_1M = ', bbp_1M)

                bbl_5M = df5['BBL_14_2.0'].tail(1).item()
                bbm_5M = df5['BBM_14_2.0'].tail(1).item()
                bbu_5M = df5['BBU_14_2.0'].tail(1).item()
                bbb_5M = df5['BBB_14_2.0'].tail(1).item()
                bbp_5M = df5['BBP_14_2.0'].tail(1).item()

                df5 = df5.drop(columns=['BBL_14_2.0'])
                df5 = df5.drop(columns=['BBM_14_2.0'])
                df5 = df5.drop(columns=['BBU_14_2.0'])
                df5 = df5.drop(columns=['BBB_14_2.0'])
                df5 = df5.drop(columns=['BBP_14_2.0'])

                #print('bbl_5M = ', bbl_5M)
                #print('bbm_5M = ', bbm_5M)
                #print('bbu_5M = ', bbu_5M)
                #print('bbb_5M = ', bbb_5M)
                #print('bbp_5M = ', bbp_5M)

                close = df['close'].tail(1).item()
                Val_1M_SMA3 = ta.sma(df['close'], length=3).tail(1).item()
                '''


        i += 1
        print('Bars Run: ', i)
    client.run(handle_msg)

