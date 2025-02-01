from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List
import pandas as pd
import pandas_ta as ta
import time

# client = WebSocketClient("XXXXXX") # hardcoded api_key is used
client = WebSocketClient("YOUR_API_KEY")  # POLYGON_API_KEY environment variable is used

# docs
# https://polygon.io/docs/stocks/ws_stocks_am
# https://polygon-api-client.readthedocs.io/en/latest/WebSocket.html#

# aggregates (per minute)
# client.subscribe("AM.*") # all aggregates
#client.subscribe("AM.NVDA") # single ticker

# aggregates (per second)
# client.subscribe("A.*")  # all aggregates
client.subscribe("A.NVDA") # single ticker

# trades
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

# quotes
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers

sec_aggs = []
min_aggs = []
def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        #print(m)
        #bars = m
        if m.event_type == 'A':         # seconds data
            sec_aggs.append(m)
            sec_df = pd.DataFrame(sec_aggs, columns=['open', 'high', 'low', 'close', 'volume', 'end_timestamp', 'symbol', 'event_type'])
            print(sec_df.tail(1).end_timestamp)
            #print(' ')

        obj = time.gmtime(0)
        epoch = time.asctime(obj)
        #print("The epoch is:", epoch)
        curr_time = round(time.time() * 1000)
        print("Milliseconds since epoch:", curr_time)


        #if m.event_type == 'AM':        # minutes data
        #    min_aggs.append(m)
        #    min_df = pd.DataFrame(min_aggs, columns=['open', 'high', 'low', 'close', 'volume', 'end_timestamp', 'symbol', 'event_type'])
        #    #print(min_df.tail(1))
        #    #print('**************************************************************')

        #result = ta.sma(sec_df['close'],length=3)
        #print(result)




client.run(handle_msg)