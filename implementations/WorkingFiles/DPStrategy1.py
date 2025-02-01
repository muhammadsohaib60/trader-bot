


def DPS1:
# Long Enter
if (True
        and (close < bb m -diff).any()
        and sma14 > sma50
        and sma50 > sma200
        and InLong == False
        and InShort == False):
    LEnterPrice = nextopen
    # print('Enter Long Time&Price:', timestamp, LEnterPrice)
    # keyboard.press_and_release('+') #get err done, in Long
    InLong = True
    LongTradeCount += 1

# Long Exit
if ((True
     and close > bb m +diff).any()
        and InLong == True):

    LExitPrice = nextopen
    # print('Exit Long Time&Price:', timestamp, LExitPrice)

    LGain = 100 * (LExitPrice - LEnterPrice)           # assume 100 shares for now
    LSumGain += LGain
    if LGain >= 0:
        LongProfitableCount += 1
    # print('Long Trade Gain = ', LGain)
    # keyboard.press_and_release('-') #get out of Long position
    InLong = False

# Short Enter
if ((True
     and close > bbm + diff).any()
        and sma14 < sma50
        and sma50 < sma200
        and InLong == False
        and InShort == False):

    SEnterPrice = nextopen
    # print('Enter Short Time&Price:', timestamp, SEnterPrice)
    # keyboard.press_and_release('*') #short
    InShort = True
    ShortTradeCount += 1

# Short Exit
if ((True
     and close < bbm - diff).any()
        and InShort == True):

    SExitPrice = nextopen
    # print('Exit Short Time&Price:', timestamp, SExitPrice)

    SGain = 100 * (SEnterPrice - SExitPrice)  # assume 100 shares for now
    SSumGain += SGain
    if SGain >= 0:
        ShortProfitableCount += 1
    # keyboard.press_and_release('+')  # eliminate short and get even with one Long
    # print('Short Trade Gain = ', SGain)
    # print('Long Trade SumGain = ', SumGain)
    # print(' ')
    InShort = False

