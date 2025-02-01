from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List
import pandas as pd
import pandas_ta as ta
import sys

pd.options.display.width = 0
pd.set_option('display.max_rows', 40)
pd.set_option('display.min_rows', 20)

# client = WebSocketClient("XXXXXX") # hardcoded api_key is used
client = WebSocketClient("YOUR_API_KEY")  # DEV ENV KEY - POLYGON_API_KEY environment variable is used
#client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY - POLYGON_API_KEY environment variable is used


# docs
# https://polygon.io/docs/stocks/ws_stocks_am
# https://polygon-api-client.readthedocs.io/en/latest/WebSocket.html#

# aggregates (per minute)
# client.subscribe("AM.*") # all aggregates
#client.subscribe("AM.NVDA") # single ticker

# aggregates (per second)
#client.subscribe("A.*")  # all aggregates
client.subscribe("AM.NVDA") # single ticker

# trades
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

# quotes
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers



def handle_msg(msgs: List[WebSocketMessage]):    #message handler function for clients as subscribed

    for m in msgs:
        print(m)

client.run(handle_msg)

