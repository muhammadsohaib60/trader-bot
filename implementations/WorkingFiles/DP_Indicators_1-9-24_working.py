import pandas as pd
import pandas_ta as ta


class StockData:     # class to encapsulate price data and indicators, and allow multi bar timing
    def __init__(self):
        # Initialize the DataFrame or load data here
        self.df = pd.DataFrame()

    def load_data(self, existing_df):
        self.df = existing_df

    def open(self, timestamp):
        value = self.df.loc[timestamp, 'open']
        return value
    def high(self, timestamp):
        value = self.df.loc[timestamp, 'high']
        return value
    def low(self, timestamp):
        value = self.df.loc[timestamp, 'low']
        return value
    def close(self, timestamp):
        value = self.df.loc[timestamp, 'close']
        return value
    def vwap(self, timestamp):
        value = self.df.loc[timestamp, 'vwap']
        return value
    def volume(self, timestamp):
        value = self.df.loc[timestamp, 'volume']
        return value
    def SMA3(self, timestamp):
        value = self.df.loc[timestamp, 'SMA3']
        return value
    def SL_SMA3(self, timestamp):
        value = self.df.loc[timestamp, 'Sl_SMA3']
        return value
    def SMA14(self, timestamp):
        value = self.df.loc[timestamp, 'SMA14']
        return value
    def SL_SMA14(self, timestamp):
        value = self.df.loc[timestamp, 'Sl_SMA14']
        return value
    def SMA50(self, timestamp):
        value = self.df.loc[timestamp, 'SMA50']
        return value
    def SL_SMA50(self, timestamp):
        value = self.df.loc[timestamp, 'Sl_SMA50']
        return value
    def SMA200(self, timestamp):
        value = self.df.loc[timestamp, 'SMA200']
        return value
    def SL_SMA200(self, timestamp):
        value = self.df.loc[timestamp, 'Sl_SMA200']
        return value
    def BBL_14_2(self, timestamp):
        value = self.df.loc[timestamp, 'BBL_14_2']
        return value
    def BBM_14_2(self, timestamp):
        value = self.df.loc[timestamp, 'BBM_14_2']
        return value
    def BBU_14_2(self, timestamp):
        value = self.df.loc[timestamp, 'BBU_14_2']
        return value
    def BBB_14_2(self, timestamp):
        value = self.df.loc[timestamp, 'BBB_14_2']
        return value
    def BBP_14_2(self, timestamp):
        value = self.df.loc[timestamp, 'BBP_14_2']
        return value
    def typical(self, timestamp):
        value = (   self.df.loc[timestamp, 'open'] +
                    self.df.loc[timestamp, 'close'] +
                    self.df.loc[timestamp, 'high'] +
                    self.df.loc[timestamp, 'low'] ) / 4
        return value
    #def time(self):
    #    #value = self.df.iloc[-1].index.strftime('%H:%M:%S')
    #    #value = self.df.iloc[-1].index.time()
    #    value = self.df.iloc[-1].index.strftime('%Y-%m-%d %H:%M:%S')
    #    return value


#********************************
def Expand_1minute_Data(df):

    df['SMA3'] = df.ta.sma(length=3)
    # df['SMA3_1M'] = ta.sma(df['close'], length=3)
    df['Sl_SMA3'] = ta.slope(ta.sma(df['close'], length=3), length=1)
    df['SMA14'] = ta.sma(df['close'], length=14)
    df['Sl_SMA14'] = ta.slope(ta.sma(df['close'], length=14), length=1)
    df['SMA50'] = ta.sma(df['close'], length=50)
    df['Sl_SMA50'] = ta.slope(ta.sma(df['close'], length=50), length=1)
    df['SMA200'] = ta.sma(df['close'], length=200)
    df['Sl_SMA200'] = ta.slope(ta.sma(df['close'], length=200), length=1)

    bb = ta.bbands(df['close'], length=14, std=2)
    df = pd.concat([df, bb], axis=1)
    df = df.rename(columns={'BBL_14_2.0': 'BBL_14_2'})
    df = df.rename(columns={'BBM_14_2.0': 'BBM_14_2'})
    df = df.rename(columns={'BBU_14_2.0': 'BBU_14_2'})
    df = df.rename(columns={'BBB_14_2.0': 'BBB_14_2'})
    df = df.rename(columns={'BBP_14_2.0': 'BBP_14_2'})

    # resample and set up 5 min bars
    df5 = df.resample("5min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df5)

    # print(df)
    df5['SMA3'] = ta.sma(df5['close'], length=3)
    df5['Sl_SMA3'] = ta.slope(ta.sma(df5['close'], length=3), length=1)
    df5['SMA14'] = ta.sma(df5['close'], length=14)
    df5['Sl_SMA14'] = ta.slope(ta.sma(df5['close'], length=14), length=1)
    df5['SMA50'] = ta.sma(df5['close'], length=50)
    df5['Sl_SMA50'] = ta.slope(ta.sma(df5['close'], length=50), length=1)
    df5['SMA200'] = ta.sma(df5['close'], length=200)
    df5['Sl_SMA200'] = ta.slope(ta.sma(df5['close'], length=200), length=1)
    # print(df5)

    bb5 = ta.bbands(df5['close'], length=14, std=2)
    df5 = pd.concat([df5, bb5], axis=1)
    df5 = df5.rename(columns={'BBL_14_2.0': 'BBL_14_2'})
    df5 = df5.rename(columns={'BBM_14_2.0': 'BBM_14_2'})
    df5 = df5.rename(columns={'BBU_14_2.0': 'BBU_14_2'})
    df5 = df5.rename(columns={'BBB_14_2.0': 'BBB_14_2'})
    df5 = df5.rename(columns={'BBP_14_2.0': 'BBP_14_2'})

    # resample and set up 15 min bars
    df15 = df.resample("15min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "vwap": "last",
        "volume": "sum", "timestamp": "last"})
    # print(df15)

    df15['SMA3'] = ta.sma(df15['close'], length=3)
    df15['Sl_SMA3'] = ta.slope(ta.sma(df15['close'], length=3), length=1)
    df15['SMA14'] = ta.sma(df15['close'], length=14)
    df15['Sl_SMA14'] = ta.slope(ta.sma(df15['close'], length=14), length=1)
    df15['SMA50'] = ta.sma(df15['close'], length=50)
    df15['Sl_SMA50'] = ta.slope(ta.sma(df15['close'], length=50), length=1)
    df15['SMA200'] = ta.sma(df15['close'], length=200)
    df15['Sl_SMA200'] = ta.slope(ta.sma(df15['close'], length=200), length=1)
    # print(df15)

    bb15 = ta.bbands(df15['close'], length=14, std=2)
    df15 = pd.concat([df15, bb15], axis=1)
    df15 = df15.rename(columns={'BBL_14_2.0': 'BBL_14_2'})
    df15 = df15.rename(columns={'BBM_14_2.0': 'BBM_14_2'})
    df15 = df15.rename(columns={'BBU_14_2.0': 'BBU_14_2'})
    df15 = df15.rename(columns={'BBB_14_2.0': 'BBB_14_2'})
    df15 = df15.rename(columns={'BBP_14_2.0': 'BBP_14_2'})

    return df, df5, df15



