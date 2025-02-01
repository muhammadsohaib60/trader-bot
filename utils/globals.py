import pandas as pd

global ltotal_gain
global stotal_gain

df1min = 0

LiveTradeActive = False
PlotOutputStd = False

BackTest = True
PlotOutputHA = False
UseOptimizer = False
PrintStrategyTrades = True

HistBeginDateTime = '2024-01-19 07:00:00'
HistEndDateTime = '2024-01-19 15:00:00'
num_lookback_day_1day_chart = 60


Ticker = ('NVDA')
NumShares = 100
in_long = False
in_short = False

lentry_price = 0
lexit_price = 0
ltrade_gain = 0
ltotal_gain = 0

sentry_price = 0
sexit_price = 0
strade_gain = 0
stotal_gain = 0

program_running = True
dfD1 = pd.DataFrame

