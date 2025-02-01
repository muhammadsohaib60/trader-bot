from polygon import RESTClient
import pandas as pd
import pandas_ta as ta
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List


pd.options.display.width = 0
pd.set_option('display.max_rows', 40)
pd.set_option('display.min_rows', 20)

sec_aggs = []    # init list of seconds timeframe aggregate messages
min_aggs = []    # init list of minutes timeframe aggregate messages

# First get historical Data and parse

client = RESTClient("YOUR_API_KEY")

aggs = []

for a in client.list_aggs(
    "NVDA",
    1,
    "minute",
    "2023-12-28",    # YYYY-MM-DD
    "2023-12-28",
    limit=50000,
    ):
    aggs.append(a)

#print(aggs)

#df=pd.DataFrame(aggs)
#global df
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

df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'volume', 'timestamp'])
df.sort_values(by='timestamp', inplace = True)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
df.set_index("datetime", inplace=True)      #index with date time as index axis
# df = df.drop(columns=['timestamp'])
# print(df)

# Next Get Streaming Real-Time Data and parse

client = WebSocketClient("YOUR_API_KEY")  # DEV ENV KEY - POLYGON_API_KEY environment variable is used
# aggregates (per minute)
# client.subscribe("AM.*") # all aggregates
client.subscribe("AM.QQQ") # single ticker

# aggregates (per second)
# client.subscribe("A.*")  # all aggregates
# client.subscribe("A.NRXP") # single ticker


while True:     # now handle websocket for continuous real-time messages (break out to exit)
    def handle_msg(msgs: List[WebSocketMessage]):  # message handler function for clients as subscribed

        # Init
        #global df
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
                                      columns=['open', 'high', 'low', 'close', 'volume', 'end_timestamp'])

                dfRT['timestamp'] = dfRT['end_timestamp']
                dfRT= dfRT.drop(columns=['end_timestamp'])
                dfRT['datetime'] = pd.to_datetime(dfRT['timestamp'], unit='ms') - pd.Timedelta(hours=7)
                dfRT.set_index("datetime", inplace=True)  # index with date time as index axis
                Hdfcopy = pd.concat([df, dfRT])
                Hdf = Hdfcopy.resample('1T').ffill(limit=30)
                print(Hdf)

                # 5 min bars
                df5 = df.resample("5min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum"})
                # print(df5)

                # 15 min bars
                df15 = df.resample("15min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum"})

                # day bars
                dfd = df.resample("1D").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum"})

                #Set up main indicators for use
                Slope_1M_SMA3 = ta.slope(ta.sma(df['close'], length=3), length=1)
                Slope_5M_SMA3 = ta.slope(ta.sma(df5['close'], length=3), length=1)
                Slope_15M_SMA3 = ta.slope(ta.sma(df15['close'], length=3), length=1)
                Slope_1D_SMA3 = ta.slope(ta.sma(dfd['close'], length=3), length=1)
                #print(Slope_1M_SMA3.tail(1).item())
                bb = ta.bbands(df['close'], length=14, std=2).astype(float).round(3)
                df = pd.concat([df, bb], axis=1)
                bb5 = ta.bbands(df5['close'], length=14, std=2).astype(float).round(3)
                df5 = pd.concat([df5, bb5], axis=1)
                #print(df)

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

                # Long Enter
                if  ( False
                    and close > Val_1M_SMA3
                    and Slope_1M_SMA3.tail(1).item() >= 0
                    and Slope_5M_SMA3.tail(1).item() >= 0
                    and bbp_1M < 0.9
                    and bbp_5M < 0.9
                    #and Slope_15M_SMA3.tail(1).item() >= 0
                    #and Slope_1D_SMA3.tail(1).item() >= 0
                    and InLong == False
                    and InShort == False
                    ):
                    LEnterPrice = close
                    print('Enter Long Price:', LEnterPrice)
                    # keyboard.press_and_release('+') #get err done, in Long
                    InLong = True
                    LongTradeCount += 1

                # Long Exit
                if (((False and (close > LEnterPrice + ProfitDelta)
                    or (close < LEnterPrice - StopLossDelta))
                    and InLong == True)):
                    LExitPrice = close
                    print('Enter Long Price:', LEnterPrice)
                    print('Exit Long Price:', LExitPrice)
                    LGain = 100 * (LExitPrice - LEnterPrice)  # assume 100 shares for now
                    LSumGain += LGain
                    if LGain >= 0:
                        LongProfitableCount += 1
                        # print('Long Trade Gain = ', LGain)
                        # keyboard.press_and_release('-') #get out of Long position
                        InLong = False

                    # Print a summary of the main metrics for consideration
                    print(' ')
                    print('*********************************************')
                    print('**************   Summary   ******************')
                    print('*********************************************')
                    print(f'Sum of Long Gains: \t\t\t\t\t${LSumGain:.2f}')
                    print('Number of Long Trades: \t\t\t\t', LongTradeCount)
                    if LongTradeCount != 0:
                        print(f'Average gain per Long Trade: \t\t${LSumGain / LongTradeCount:.2f}')
                        print(f'Long % Profitable: \t\t\t\t\t{100 * LongProfitableCount / LongTradeCount:.1f} %')
                    else:
                        print(f'Average gain per Long Trade: \t\t${0:.2f}')
                        print(f'Long % Profitable: \t\t\t\t\t{100 * 0:.1f} %')

                    print(f'Sum of Short Gains: \t\t\t\t${SSumGain:.2f}')
                    print('Number of Short Trades: \t\t\t', ShortTradeCount)
                    if ShortTradeCount != 0:
                        print(f'Average gain per Short Trade: \t\t${SSumGain / ShortTradeCount:.2f}')
                        print(f'Short % Profitable:\t\t\t\t\t{100 * ShortProfitableCount / ShortTradeCount:.1f} %')
                    else:
                        print(f'Average gain per Short Trade: \t\t${0:.2f}')
                        print(f'Short % Profitable:\t\t\t\t\t{0:.1f} %')

                    print('Number of All Trades: \t\t\t\t', LongTradeCount + ShortTradeCount)
                    if LongTradeCount + ShortTradeCount != 0:
                        print(
                            f'Average gain for All Trades: \t\t${(LSumGain + SSumGain) / (LongTradeCount + ShortTradeCount):.2f}')
                    else:
                        print(f'Average gain for All Trades: \t\t${0:.2f}')
                    print(f'Sum of All Gains: \t\t\t\t\t${LSumGain + SSumGain:.2f}')
                    print('*********************************************')




                if False:
                    # Test plot of df for debug status
                    fig=plt.figure()
                    fig.tight_layout()
                    ax1 = fig.add_subplot(1,4,1)
                    ax2 = fig.add_subplot(1,4,2)
                    ax3 = fig.add_subplot(1, 4, 3)
                    ax4 = fig.add_subplot(1, 4, 4)
                    plt.ion()
                    ax1.plot(df.index, df['close'], marker='.', linestyle='-', color='blue')
                    ax2.plot(df5.index, df5['close'], marker='.', linestyle='-', color='green')
                    ax3.plot(df15.index, df15['close'], marker='.', linestyle='-', color='red')
                    ax4.plot(dfd.index, dfd['close'], marker='.', linestyle='-', color='orange')
                    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                                        wspace=0.35)
                    plt.pause(1)
                    #plt.ioff()
                    #plt.show()  # This will keep the plot window open for infinity seconds

                if False:
                    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                                     open=df.open,
                                                     high=df.high,
                                                     low=df.low,
                                                     close=df.close
                                                     )])
                    fig.update_traces(name= 'NVDA', selector = dict(type='candlestick'))
                    fig.update_layout(width= 2500)

                    fig.show()






        i += 1
        print('Bars Run: ', i)
    client.run(handle_msg)

