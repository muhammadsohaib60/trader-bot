import time
import pandas as pd
import pandas_ta as ta
from DP_Indicators import Expand_1minute_Data, StockData
from SchwabBrokerInterface import Buy, Sell, Short, CancelAll, CloseAll
import winsound
from globals import (PlotOutputStd, PlotOutputHA, BackTest, LiveTradeActive,
                         Ticker, HistBeginDateTime, HistEndDateTime, entry_price, exit_price,
                         trade_gain, total_gain, in_long, in_short)

def LSimpleStrategy1(LiveTradeActive, dt, stock_data_1, stock_data_5, stock_data_15):
    global in_long, in_short, entry_price, exit_price, trade_gain, total_gain
    #set up tones params for audio alerts:
    high_frequency = 1500  # Set Frequency To 2500 Hertz
    low_frequency = 500  # Set Frequency To 1000 Hertz
    duration = 500  # Set Duration To 500 ms == 0.5 second


    if (True and        # This is a Long Runner Form Strategy
        in_long == False and
        stock_data_1.close(dt) > stock_data_1.SMA14(dt) and
        stock_data_1.SMA14(dt) > stock_data_1.SMA50(dt) and
        stock_data_1.SL_SMA14(dt) > stock_data_1.SL_SMA50(dt) and
        stock_data_1.SL_SMA50(dt) > stock_data_1.SL_SMA200(dt) and
        stock_data_1.SL_SMA200(dt) > -0.1 and
        stock_data_1.SL_SMA3(dt) > 0 and
        stock_data_1.BBP_14_2(dt) < 0.9
        #stock_data_5.BBP_14_2(dt) < 0.9
        ):
        in_long = True
        entry_price = stock_data_1.close(dt)
        print('*** L1 Buy *** at time :', dt, ' for entry price ', entry_price)
        if LiveTradeActive:
            Buy()
            winsound.Beep(high_frequency, duration)

    elif (False and        # This is a cross Form Strategy
        in_long == False and
        stock_data_1.low(dt) < stock_data_1.SMA14(dt) and
        stock_data_1.high(dt) > stock_data_1.SMA14(dt) and
        stock_data_1.volume(dt) > 50000 and
        stock_data_1.BBP_14_2(dt) < 0.9
        #stock_data_5.BBP_14_2(dt) < 0.9
        ):
        in_long = True
        entry_price = stock_data_1.close(dt)
        print('*** L2 Buy *** at time :', dt, ' for entry price ', entry_price)
        if LiveTradeActive:
            Buy()
            winsound.Beep(high_frequency, duration)


    elif (True and                  # exit on downer
        in_long == True and
        stock_data_1.close(dt) < stock_data_1.SMA3(dt) and
        stock_data_1.SMA3(dt) < stock_data_1.SMA14(dt) and
        stock_data_1.SL_SMA3(dt) < 0
        ):
        in_long = False
        exit_price = stock_data_1.close(dt)
        trade_gain = (exit_price - entry_price) * 100
        total_gain += trade_gain
        print('*** L3 Sell *** at time :', dt, ' for exit price ', exit_price)
        print('Trade_Gain: ${:.2f} Total_Gain: ${:.2f}'.format(trade_gain, total_gain))
        print(' ')
        if LiveTradeActive:
            CloseAll()
            winsound.Beep(low_frequency, duration)

    elif (True and  # exit on downer
          in_long == True and
          stock_data_1.BBP_14_2(dt) > 0.99
          ):
        in_long = False
        exit_price = stock_data_1.close(dt)
        trade_gain = (exit_price - entry_price) * 100
        total_gain += trade_gain
        print('*** L4 Sell *** at time :', dt, ' for exit price ', exit_price)
        print('Trade_Gain: ${:.2f} Total_Gain: ${:.2f}'.format(trade_gain, total_gain))
        print(' ')
        print(' ')
        if LiveTradeActive:
            CloseAll()
            winsound.Beep(low_frequency, duration)

    elif (True and  # exit on top of BB
          in_long == True and
          stock_data_1.SL_SMA3(dt) < 0.05 and
          stock_data_1.BBP_14_2(dt) < 0.7
          ):
        in_long = False
        exit_price = stock_data_1.close(dt)
        trade_gain = (exit_price - entry_price) * 100
        total_gain += trade_gain
        print('*** L5 Sell *** at time :', dt, ' for exit price ', exit_price)
        print('Trade_Gain: ${:.2f} Total_Gain: ${:.2f}'.format(trade_gain, total_gain))
        print(' ')
        if LiveTradeActive:
            CloseAll()
            winsound.Beep(low_frequency, duration)

    #print('In_Long:',in_long, ' In_Short:', in_short, ' Total_Gain: ',total_gain*100)
    #print(f"1Min BBP is: {stock_data_1.BBP_14_2(dt):,.2f}" )
    return 1


def SSimpleStrategy1(TradeActive, dt, stock_data_1, stock_data_5, stock_data_15):
    high_frequency = 1500  # Set Frequency To 2500 Hertz
    low_frequency = 500  # Set Frequency To 1000 Hertz
    duration = 500  # Set Duration To 500 ms == 0.5 second
    from globals import (PlotOutputStd, PlotOutputHA, BackTest, LiveTradeActive,
                         Ticker, HistBeginDateTime, HistEndDateTime, in_long, in_short, entry_price, exit_price,
                         trade_gain, total_gain)


    if (True and                #This is a Short Runner Form Strategy
        in_short == False and
        stock_data_1.close(dt) < stock_data_1.SMA3(dt) and
        stock_data_1.close(dt) < stock_data_1.SMA14(dt) and
        stock_data_1.close(dt) < stock_data_1.SMA50(dt) and
        stock_data_1.SL_SMA3(dt) < -0.05 and
        stock_data_1.SL_SMA14(dt) < -0.05 and
        stock_data_1.SL_SMA50(dt) < 0.1 and
        stock_data_1.BBP_14_2(dt) > 0.15
        ):
        in_short  = True
        entry_price = stock_data_1.close()
        print('S1 Enter Short')
        if LiveTradeActive:
            Short()
            winsound.Beep(high_frequency, duration)

    elif (True and                #This is a Short Cross Form Strategy
        in_short == False and
        stock_data_1.high(dt) > stock_data_1.SMA14(dt) and
        stock_data_1.low(dt) < stock_data_1.SMA14(dt) and
        stock_data_1.volume(dt) > 50000 and
        stock_data_1.BBP_14_2(dt) > 0.15
        ):
        in_short  = True
        entry_price = stock_data_1.close(dt)
        print('S2 Enter Short')
        if LiveTradeActive:
            Short()
            winsound.Beep(high_frequency, duration)


    elif (True and                  # exit on popup
        in_short  == True and
        stock_data_1.close(dt) > stock_data_1.SMA3(dt) and
        stock_data_1.SMA3(dt) > stock_data_1.SMA14(dt) and
        stock_data_1.SL_SMA3(dt) > 0
        ):
        in_short  = False
        exit_price = stock_data_1.close(dt)
        trade_gain = entry_price - exit_price
        total_gain += trade_gain
        print('S3 Exit on Up Move (via CloseAll); Trade_Gain:', trade_gain, ' total_gain:', total_gain)
        if LiveTradeActive:
            CloseAll()
            winsound.Beep(low_frequency, duration)

    elif (True and  # exit on bot of BB
          in_short  == True and
          stock_data_1.BBP_14_2(dt) < 0.1
          ):
        in_short  = False
        exit_price = stock_data_1.close(dt)
        trade_gain = entry_price - exit_price
        total_gain += trade_gain
        print('S4 Exit on BB (via CloseAll); Trade_Gain:', trade_gain, ' total_gain:', total_gain)
        if LiveTradeActive:
            CloseAll()
            winsound.Beep(low_frequency, duration)

    return 1

total_gain = 0