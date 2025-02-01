from polygon import RESTClient
import pandas as pd
import pandas_ta as ta
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go


pd.options.display.width = 0
pd.set_option('display.max_rows', 40)
pd.set_option('display.min_rows', 20)

# docs
# https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to
# https://polygon-api-client.readthedocs.io/en/latest/Aggs.html#polygon.RESTClient.list_aggs

# API key injected below for easy use. If not provided, the script will attempt
# to use the environment variable "POLYGON_API_KEY".
#
# setx POLYGON_API_KEY "YOUR_API_KEY"   <- windows
# export POLYGON_API_KEY="<your_api_key>" <- mac/linux
#
# Note: To persist the environment variable you need to add the above command
# to the shell startup script (e.g. .bashrc or .bash_profile.
#
# client = RESTClient("XXXXXX") # hardcoded api_key is used
client = RESTClient("YOUR_API_KEY")  # POLYGON_API_KEY environment variable is used


NetGainList = []
aggs = []

for a in client.list_aggs(
    "NVDA",
    1,
    "minute",
    "2023-12-11",    # YYYY-MM-DD
    "2023-12-15",
    limit=50000,
    ):
    aggs.append(a)

#print(aggs)

#df=pd.DataFrame(aggs)

df = pd.DataFrame(aggs, columns=['open', 'high', 'low', 'close', 'volume', 'vwap', 'timestamp'])
df.sort_values(by='timestamp', inplace = True)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
#print(df)

# 1 min bars
df.set_index("datetime", inplace=True)      #index with date time as index axis

# 5 min bars
df5 = df.resample("5min").agg({
    "open":"first",
    "high":"max",
    "low":"min",
    "close":"last",
    "volume":"sum" })
#print(df5)

# 15 min bars
df15 = df.resample("15min").agg({
    "open":"first",
    "high":"max",
    "low":"min",
    "close":"last",
    "volume":"sum" })

# day bars
dfd = df.resample("1D").agg({
    "open":"first",
    "high":"max",
    "low":"min",
    "close":"last",
    "volume":"sum" })


fig=plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)

plt.ion()

ax1.plot(df.index, df['close'], marker='.', linestyle='-')
ax2.plot(df.index, ta.slope(df['close'], length=3), marker='.', linestyle='-')

plt.pause(5)
plt.ioff()
plt.show()  # This will keep the plot window open for infinity seconds




'''
fig=plt.figure()
ax1 = fig.add_subplot(1,4,1)
ax2 = fig.add_subplot(1,4,2)
ax3 = fig.add_subplot(1,4,3)
ax4 = fig.add_subplot(1,4,4)
plt.ion()
ax4.plot(df.index, df['close'], marker='.', linestyle='-')
plt.title('1min')

ax3.plot(df5.index, df5['close'], marker='.', linestyle='-')
ax2.plot(df15.index, df15['close'], marker='.', linestyle='-')
ax1.plot(dfd.index, dfd['close'], marker='.', linestyle='-')

#ax1.plt(df['close'])
#plt.xlabel('Date')
#plt.ylabel('Close Price')
#plt.title('1min')

plt.pause(5)
plt.ioff()
plt.show()  # This will keep the plot window open for infinity seconds
'''


'''
# This plot uses "go" library, and shows candles and more features
fig = go.Figure(data = [go.Candlestick(x = df.index,
                                       open = df.open,
                                       high = df.high,
                                       low = df.low,
                                       close = df.close
                                       )])
fig.show()
'''