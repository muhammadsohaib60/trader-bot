from polygon import RESTClient
import pandas as pd
from typing import List
import pandas_ta as ta
import datetime

pd.options.display.width = 0
pd.set_option('display.max_rows', 40)
pd.set_option('display.min_rows', 20)

# docs
# https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to
# https://polygon-api-client.readthedocs.io/en/latest/Aggs.html#polygon.RESTClient.list_aggs

# API key injected below for easy use. If not provided, the script will attempt
# to use the environment variable "POLYGON_API_KEY".
#
# setx POLYGON_API_KEY "<your_api_key>"   <- windows
# export POLYGON_API_KEY="<your_api_key>" <- mac/linux
#
# Note: To persist the environment variable you need to add the above command
# to the shell startup script (e.g. .bashrc or .bash_profile.
#
# client = RESTClient("XXXXXX") # hardcoded api_key is used
client = RESTClient("YOUR_API_KEY")  # POLYGON_API_KEY environment variable is used

aggs = []
for a in client.list_aggs(
    "NVDA",
    1,
    "minute",
    "2023-12-01",
    "2023-12-08",
    limit=50000,
    ):
    aggs.append(a)

#print(aggs)

#df=pd.DataFrame(aggs)

df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'volume', 'vwap', 'timestamp'])
#df.sort_values(by='timestamp', inplace = True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
#print(df)

df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['close'] = df['close'].astype(float)
df['vwap'] = df['vwap'].astype(float)

sma3 = ta.sma(df['close'],length=3).astype(float).round(3)
sma5 = ta.sma(df['close'],length=5).astype(float).round(3)
sma8 = ta.sma(df['close'],length=8).astype(float).round(3)
sma10 = ta.sma(df['close'],length=10).astype(float).round(3)
sma14 = ta.sma(df['close'],length=14).astype(float).round(3)
sma21 = ta.sma(df['close'],length=21).astype(float).round(3)
sma50 = ta.sma(df['close'],length=50).astype(float).round(3)
sma200 = ta.sma(df['close'],length=200).astype(float).round(3)
bb = ta.bbands(df['close'],length=14, std=2).astype(float).round(3)
#slope = ta.slope(df['close'],length=1)
#slope = ta.slope(sma3,length=2)

df = pd.concat([df, sma3, sma5, sma8, sma10, sma14, sma21, sma50, sma200, bb], axis=1)
#print(df)

open = df.iloc[-1]['open']
high = df.iloc[-1]['high']
low = df.iloc[-1]['low']
close = df.iloc[-1]['close']
volume = df.iloc[-1]['volume']
vwap = df.iloc[-1]['vwap']
timestamp = df.iloc[-1]['timestamp']
sma3 = df.iloc[-1]['SMA_3']
sma5 = df.iloc[-1]['SMA_5']
sma8 = df.iloc[-1]['SMA_8']
sma10 = df.iloc[-1]['SMA_10']
sma14 = df.iloc[-1]['SMA_14']
sma21 = df.iloc[-1]['SMA_21']
sma50 = df.iloc[-1]['SMA_50']
sma200 = df.iloc[-1]['SMA_200']
bbl = df.iloc[-1]['BBL_14_2.0']
bbm = df.iloc[-1]['BBM_14_2.0']
bbu = df.iloc[-1]['BBU_14_2.0']

# Init
InLong = False
InShort = False
LGain = 0
SGain = 0
LSumGain = 0
SSumGain = 0
SumGain = 0
LongTradeCount = 0
ShortTradeCount = 0

for i in range(len(df)):    #Loop Through the ticker dataframe samples

    open = df.iloc[i]['open']
    high = df.iloc[i]['high']
    low = df.iloc[i]['low']
    close = df.iloc[i]['close']
    volume = df.iloc[i]['volume']
    vwap = df.iloc[i]['vwap']
    timestamp = df.iloc[i]['timestamp']
    sma3 = df.iloc[i]['SMA_3']
    sma5 = df.iloc[i]['SMA_5']
    sma8 = df.iloc[i]['SMA_8']
    sma10 = df.iloc[i]['SMA_10']
    sma14 = df.iloc[i]['SMA_14']
    sma21 = df.iloc[i]['SMA_21']
    sma50 = df.iloc[i]['SMA_50']
    sma200 = df.iloc[i]['SMA_200']
    bbl = df.iloc[i]['BBL_14_2.0']
    bbm = df.iloc[i]['BBM_14_2.0']
    bbu = df.iloc[i]['BBU_14_2.0']


    diff = 0.22

    # ********* Start Simple Trading Algo *************
    #print('BBM is:', bbm)
    #print('Close is:', close)

    #Long Enter
    if ((close < bbm-diff).any() and sma50 > sma200 and InLong == False and InShort == False):
        LEnterPrice = close
        print('Enter Long Time&Price:', timestamp, LEnterPrice)
        InLong = True
        LongTradeCount += 1

    #Long Exit
    if (close > bbm+diff).any() and InLong == True:
        LExitPrice = close
        print('Exit Long Time&Price:', timestamp, LExitPrice)

        LGain = 100 * (LExitPrice - LEnterPrice)           #assume 100 shares for now
        LSumGain += LGain
        print('Long Trade Gain = ', LGain)
        InLong = False

    # Short Enter
    if (close > bbm + diff).any() and sma50 < sma200 and InLong == False and InShort == False:
        SEnterPrice = close
        print('Enter Short Time&Price:', timestamp, SEnterPrice)
        InShort = True
        ShortTradeCount += 1

    # Short Exit
    if (close < bbm - diff).any() and InShort == True:
        SExitPrice = close
        print('Exit Short Time&Price:', timestamp, SExitPrice)

        SGain = 100 * (SEnterPrice - SExitPrice)  # assume 100 shares for now
        SSumGain += SGain
        print('Short Trade Gain = ', SGain)
        # print('Long Trade SumGain = ', SumGain)
        print(' ')
        InShort = False



    # print( open, high, low, close, volume, vwap, timestamp )       #prototype - get the latest data for close
    # print( sma3, sma5, sma8, sma10, sma14, sma21, sma50, sma200, bbl, bbm, bbu )
    # print(df.iloc[-1]['SMA_3'] )

    # print(df.iloc[-1])

print(' ')
print('*********************************************')
print('**************   Summary   ******************')
print('*********************************************')
print(f'Sum of Long Gains: \t\t\t\t\t${LSumGain:.2f}')
print('Number of Long Trades: \t\t\t\t', LongTradeCount)
print(f'Average gain per Long Trade: \t\t${LSumGain/LongTradeCount:.2f}')
print(f'Sum of Short Gains: \t\t\t\t${SSumGain:.2f}')
print('Number of Short Trades: \t\t\t', ShortTradeCount)
print(f'Average gain per Short Trade: \t\t${SSumGain/ShortTradeCount:.2f}')
print(f'Sum of All Gains: \t\t\t\t\t${LSumGain+SSumGain:.2f}')
print('Number of All Trades: \t\t\t\t', LongTradeCount+ShortTradeCount)
print(f'Average gain for All Trades: \t\t${(LSumGain+SSumGain)/(LongTradeCount+ShortTradeCount):.2f}')
print('*********************************************')