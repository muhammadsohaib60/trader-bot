from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from typing import List
import pandas as pd

# client = WebSocketClient("XXXXXX") # hardcoded api_key is used
#client = WebSocketClient("YOUR_API_KEY")  # POLYGON_API_KEY environment variable is used
client = WebSocketClient("6H8Lc8WQkYoX2BURIOJkqFID9rImFYop")  # TEST ENV KEY - POLYGON_API_KEY environment variable is used


# docs
# https://polygon.io/docs/stocks/ws_stocks_am
# https://polygon-api-client.readthedocs.io/en/latest/WebSocket.html#

# aggregates (per minute)
# client.subscribe("AM.*") # all aggregates
# client.subscribe("AM.NVDA") # single ticker

# aggregates (per second)
client.subscribe("A.*")  # all aggregates
#client.subscribe("A.NVDA") # single ticker

# trades
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

# quotes
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers

aggs = []

def handle_msg(msgs: List[WebSocketMessage]):

    for m in msgs:
        # print(m)

        if m.event_type == 'A':  # per sec msgs
            aggs.append(m)
            df = pd.DataFrame(aggs,
                                    columns=['symbol', 'open', 'high', 'low', 'close', 'volume', 'end_timestamp'])
            print(df)


# print messages
client.run(handle_msg)