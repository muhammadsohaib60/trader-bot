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
# client.subscribe("A.*")  # all aggregates
client.subscribe("A.NVDA") # single ticker

# trades
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

# quotes
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers

sec_aggs = []    # init list of seconds timeframe aggregate messages
min_aggs = []    # init list of minutes timeframe aggregate messages
InLong = False
InShort = False
LEnterPrice = 0
LExitPrice = 0
SEnterPrice = 0
SExitPrice = 0
LGain = 0
SGain = 0
LSumGain = 0
SSumGain = 0

def handle_msg(msgs: List[WebSocketMessage]):    #message handler function for clients as subscribed

    # Init
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
    SumGain = 0
    LongTradeCount = 0
    ShortTradeCount = 0
    LongProfitableCount = 0
    ShortProfitableCount = 0
    AlgosRunning = False
    open = 0
    high = 0
    low = 0
    close = 0
    volume = 0
    diff = 0.09

    for m in msgs:
        print(m)

        if m.event_type == 'A':    #per sec msgs
            sec_aggs.append(m)
            sec_df = pd.DataFrame(sec_aggs, columns=['open', 'high', 'low', 'close', 'volume', 'end_timestamp', 'symbol', 'event_type'])
            sec_df['timestamp']=sec_df['end_timestamp']
            sec_df = sec_df.drop(columns=['end_timestamp'])
            sec_df['datetime'] = pd.to_datetime(sec_df['timestamp'], unit='ms') - pd.Timedelta(hours=7)
            # print(sec_df.tail(1))
            #print(' ')
            #print(m.close)    #to get the last value of one column

            # open_1sec = m.open
            # high_1sec = m.high
            # low_1sec = m.low
            # close_1sec = m.close
            # volume_1sec = m.volume
            # print('SYMBOL 1 sec close is: ', close_1sec)

            sec_df['open'] = sec_df['open'].astype(float).round(3)
            sec_df['high'] = sec_df['high'].astype(float).round(3)
            sec_df['low'] = sec_df['low'].astype(float).round(3)
            sec_df['close'] = sec_df['close'].astype(float).round(3)
            sec_df['volume'] = sec_df['volume'].astype(int).round(3)

            open = sec_df.iloc[-1]['open']
            high = sec_df.iloc[-1]['high']
            low = sec_df.iloc[-1]['low']
            close = sec_df.iloc[-1]['close']
            volume = sec_df.iloc[-1]['volume']

            #close = sec_df.iloc[-1]['close']

            print('Close = ',close)

            #print(sec_df.tail(1).symbol)
            #print(sec_df.iloc[-1]['symbol'])

            '''

            countdown = 50-sec_df.tail(1).index.start
            if countdown > 0:
                print('Countdown to Indicators: ', countdown)
            elif countdown == 0:
                print('--------------------------')
                print('- Begin Trading Strategy -')
                print('--------------------------')
                print('     Symbol : ', sec_df.iloc[-1]['symbol'])
                print(' ')


            if (sec_df.tail(1).index >= 50).any():
                sec_sma3 = ta.sma(sec_df['close'], length=3).astype(float).round(3)
                sec_sma5 = ta.sma(sec_df['close'], length=5).astype(float).round(3)
                sec_sma8 = ta.sma(sec_df['close'], length=8).astype(float).round(3)
                sec_sma10 = ta.sma(sec_df['close'], length=10).astype(float).round(3)
                sec_sma14 = ta.sma(sec_df['close'], length=14).astype(float).round(3)
                sec_sma21 = ta.sma(sec_df['close'], length=21).astype(float).round(3)
                sec_sma50 = ta.sma(sec_df['close'], length=50).astype(float).round(3)
                #sec_sma200 = ta.sma(sec_df['close'], length=200).astype(float).round(3)
                sec_bb = ta.bbands(sec_df['close'], length=14, std=2)
                # slope = ta.slope(sec_df['close'],length=1)
                # slope = ta.slope(sma3,length=2)
                sec_df = pd.concat([sec_df, sec_bb, sec_sma3, sec_sma5, sec_sma8, sec_sma10, sec_sma14, sec_sma21, sec_sma50], axis=1)
                #print(sec_df.tail(1))
                AlgosRunning = True

                sma3 = sec_df.iloc[-1]['SMA_3']
                sma5 = sec_df.iloc[-1]['SMA_5']
                sma8 = sec_df.iloc[-1]['SMA_8']
                sma10 = sec_df.iloc[-1]['SMA_10']
                sma14 = sec_df.iloc[-1]['SMA_14']
                sma21 = sec_df.iloc[-1]['SMA_21']
                sma50 = sec_df.iloc[-1]['SMA_50']
                #sma200 = sec_df.iloc[-1]['SMA_200']

                print('Close =', close, '\t', 'sma3 =', sma3, '\t', 'sma14 =', sma14, '\t', 'sma50 =', sma50, '\t', 'NetGain =', LSumGain+SSumGain)



                # ********* Start Simple Trading Algo *************

                
                # Long Enter
                if (        (close < sma5 - diff)
                        and (sma5 > sma14)
                        and (sma14 > sma50)
                        and InLong == False
                        and InShort == False
                        and not InLong):
                    LEnterPrice = close
                    print('     Symbol : ', sec_df.iloc[-1]['symbol'])
                    print(f'Long Entry Price:\t\t\t\t${LEnterPrice:.2f}')
                    # keyboard.press_and_release('+') #get err done, in Long
                    InLong = True
                    LongTradeCount += 1

                # Long Exit
                if ( ( (close > LEnterPrice + 3) or (close < LEnterPrice - 0.35) )
                        and InLong == True):

                    LExitPrice = close
                    print(f'Long Exit Price: \t\t\t\t${LExitPrice:.2f}')

                    LGain = 100 * (LExitPrice - LEnterPrice)  # assume 100 shares for now
                    LSumGain += LGain
                    if LGain >= 0:
                        LongProfitableCount += 1

                    print(f'Long Gain on Trade: \t\t\t${LGain:.2f}')
                    print(f'TOTAL Gain on all Trades: \t\t${LSumGain + SSumGain:.2f}')
                    print(' ')
                    # keyboard.press_and_release('-') #get out of Long position
                    InLong = False

                # Short Enter
                if ((       close > sma5 + diff)
                        and (sma5 < sma14)
                        and (sma14 < sma50)
                        and InLong == False
                        and InShort == False):
                    SEnterPrice = close
                    print('     Symbol : ', sec_df.iloc[-1]['symbol'])
                    print(f'Short Entry Price:\t\t\t\t${SEnterPrice:.2f}')
                    # keyboard.press_and_release('*') #short
                    InShort = True
                    ShortTradeCount += 1

                # Short Exit
                if ( ( (close > SEnterPrice + 0.35) or (close < SEnterPrice - 2) )
                        and InShort == True):

                    SExitPrice = close
                    print(f'Short Exit Price: \t\t\t\t${SExitPrice:.2f}')

                    SGain = 100 * (SEnterPrice - SExitPrice)  # assume 100 shares for now
                    SSumGain += SGain
                    if SGain >= 0:
                        ShortProfitableCount += 1
                    # keyboard.press_and_release('+')  # eliminate short and get even with one Long

                    print(f'Short Gain on Trade: \t\t\t${SGain:.2f}')
                    print(f'TOTAL Gain on all Trades: \t\t${LSumGain+SSumGain:.2f}')
                    print(' ')
                    InShort = False
                    
                '''





    if m.event_type == 'AM':    #per minute msgs
        min_aggs.append(m)
        min_df = pd.DataFrame(min_aggs, columns=['open', 'high', 'low', 'close', 'volume', 'end_timestamp', 'symbol', 'event_type'])
        min_df['timestamp'] = min_df['end_timestamp']
        min_df = min_df.drop(columns=['end_timestamp'])
        min_df['datetime'] = pd.to_datetime(min_df['timestamp'], unit='ms')- pd.Timedelta(hours=7)
        # print(min_df.tail(1))
        # print('**************************************************************')
        # min_df['close'] = min_df['close'].astype(float)
        # Process 1 minute data frame
        # if min_df.at[-1,'close'] > 460.0:
        # print(min_df)

        open_1min = m.open
        high_1min = m.high
        low_1min = m.low
        close_1min = m.close
        volume_1min = m.volume
        # print('********* SYMBOL 1 min close is: ',close_1min)

        if AlgosRunning == True:
            # Print a summary of the main metrics for consideration
            print(' ')
            print(' ')
            print(' ')
            print('*********************************************')
            print('**************   Summary   ******************')
            print('*********************************************')
            print(f'Sum of Long Gains: \t\t\t\t\t${LSumGain:.2f}')
            print('Number of Long Trades: \t\t\t\t', LongTradeCount)
            #print(f'Average gain per Long Trade: \t\t${LSumGain / LongTradeCount:.2f}')
            print(f'Long % Profitable: \t\t\t\t\t{100 * LongProfitableCount / LongTradeCount:.1f} %')
            print(f'Sum of Short Gains: \t\t\t\t${SSumGain:.2f}')
            print('Number of Short Trades: \t\t\t', ShortTradeCount)
            #print(f'Average gain per Short Trade: \t\t${SSumGain / ShortTradeCount:.2f}')
            print(f'Short % Profitable:\t\t\t\t\t{100 * ShortProfitableCount / ShortTradeCount:.1f} %')
            print(f'Sum of All Gains: \t\t\t\t\t${LSumGain + SSumGain:.2f}')
            print('Number of All Trades: \t\t\t\t', LongTradeCount + ShortTradeCount)
            print(f'Average gain for All Trades: \t\t${(LSumGain + SSumGain) / (LongTradeCount + ShortTradeCount):.2f}')
            print('*********************************************')
            print(' ')
            print(' ')


client.run(handle_msg)

