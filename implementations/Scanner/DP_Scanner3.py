from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List
import pandas as pd
import sys
import time
import pandas_ta as ta
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from DP_API_IN import Get_Historical, Get_HistReal, Get_Real_Time

pd.options.display.width = 0
pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 100)

# client = WebSocketClient("XXXXXX") # hardcoded api_key is used
# client = WebSocketClient("YOUR_API_KEY")  # POLYGON_API_KEY environment variable is used
client = WebSocketClient(
    "6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY - POLYGON_API_KEY environment variable is used

# docs
# https://polygon.io/docs/stocks/ws_stocks_am
# https://polygon-api-client.readthedocs.io/en/latest/WebSocket.html#

# aggregates (per minute)
client.subscribe("AM.*")  # all aggregates
# client.subscribe("AM.NVDA") # single ticker

# aggregates (per second)
#client.subscribe("A.*")  # all aggregates
# client.subscribe("A.NVDA") # single ticker

# trades
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

# quotes
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers

aggs = []
msg = []


def handle_msg(msgs: List[WebSocketMessage]):
    df2 = pd.DataFrame(aggs,
                       columns=['symbol', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'average_size', 'end_timestamp',
                                'otc', 'MF'])

    for m in msgs:
        # print(m)
        df_columns = ['symbol', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'average_size', 'end_timestamp', 'otc']
        df = pd.DataFrame(columns=df_columns)  # begin set up, so len is defined

        if (m.event_type == 'AM'):  # per sec msgs
            while len(df) <= 50:
                aggs.append(m)
                df = pd.DataFrame(aggs,
                                  columns=['symbol', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'average_size',
                                           'end_timestamp', 'otc'])

            df['MF'] = df['close'] * df['volume']
            # print(df)

            filtered_df = df[df['otc'].isna()]
            # print(filtered_df)

            sorted_df = filtered_df.sort_values(by='MF', ascending=False)
            # print(sorted_df)
            sorted_df.reset_index(drop=True, inplace=True)
            top_symbols = sorted_df.head(10)                    # get top 10
            # df2=df2+top_symbols
            # df2 = df2.head(10)
            # print(df2)
            # print(top_symbols)

            # merge volume field for any duplicates, and eliminate extra row
            merged_df = top_symbols

            merged_df = top_symbols.groupby('symbol', as_index=False).agg(
                {'open': 'first', 'high': 'first', 'low': 'first', 'close': 'first', 'vwap': 'first', 'volume': 'sum',
                 'average_size': 'first', 'end_timestamp': 'first', 'otc': 'first', 'MF': 'first'})

            merged_df = merged_df.sort_values(by='MF', ascending=False)
            merged_df.reset_index(drop=True, inplace=True)

            print(' ')
            print(merged_df)




    time.sleep(1)





client.run(handle_msg)

