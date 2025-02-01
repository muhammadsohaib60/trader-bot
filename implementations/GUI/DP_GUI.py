import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import json 


def create_candlestick_chart(df, timeframe, row, col):
    """Creates a candlestick chart with SMA and Bollinger Bands."""

    fig = go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close, name=f"{timeframe} Candlestick")
    return fig

def create_sma_trace(df, period, color, row, col):
    """Creates an SMA trace."""
    fig = go.Scatter(x=df.index, y=df[f'SMA{period}'], mode='lines', name=f'SMA{period}', line_color=color)
    return fig

def create_bollinger_band_trace(df, band_type, row, col):
    """Creates a Bollinger Band trace."""
    fig = go.Scatter(x=df.index, y=df[f'{band_type}_14_2'], mode='lines', name=f'{band_type}_14_2', line=dict(color='#56a6ae', dash='dash'))
    return fig


def create_volume_trace(df, row, col):
    """Creates a volume bar trace."""
    fig = go.Bar(x=df.index, y=df.volume, marker=dict(color='#7cadf8'), name="Volume")
    return fig


def Chart_Plot(Ticker, df, df5, df15, dfD):
    """Generates an interactive candlestick chart with volume and indicators."""

    fig = make_subplots(rows=2, cols=5, subplot_titles=['CONTROLS:', '1 Day', '15 Minute', '5 Minute', '1 Minute',
                        ' ', '1 Day Volume', '15 Min Volume', '5 Min Volume', '1 Min Volume'],
                        row_width=[0.2, 0.7], shared_yaxes=False, vertical_spacing=0.15,
                        horizontal_spacing=0.02, print_grid=False)

    timeframes = {'1 Minute': (df, 5), '5 Minute': (df5, 4), '15 Minute': (df15, 3), '1 Day': (dfD, 2)}

    for timeframe, (data, col) in timeframes.items():
        fig.add_trace(create_candlestick_chart(data, timeframe, 1, col), row=1, col=col)
        fig.add_trace(create_sma_trace(data, 3, '#ff00ff', 1, col), row=1, col=col)
        fig.add_trace(create_sma_trace(data, 14, '#ff0000', 1, col), row=1, col=col)
        fig.add_trace(create_sma_trace(data, 50, '#00ff00', 1, col), row=1, col=col)
        fig.add_trace(create_sma_trace(data, 200, '#0000ff', 1, col), row=1, col=col)
        fig.add_trace(create_bollinger_band_trace(data, 'BBL', 1, col), row=1, col=col)
        fig.add_trace(create_bollinger_band_trace(data, 'BBU', 1, col), row=1, col=col)
        fig.add_trace(create_volume_trace(data, 2, col), row=2, col=col)  # Volume on row 2
        fig.update_xaxes(title_text=f"Slider - {timeframe} Time Interval", row=1, col=col)


    def set_time_range(df, minutes):
        current_time = datetime.now()
        end_time = current_time + timedelta(minutes=minutes // 60 if minutes >= 60 else 1)  # Ensure at least 1 minute
        start_time = current_time - timedelta(minutes=minutes) if minutes < 60 else current_time - timedelta(hours=minutes//60)
        last_day = df.index[-1].date()
        start_datetime = datetime.combine(last_day, start_time.time())
        end_datetime = datetime.combine(last_day, end_time.time())
        return start_datetime, end_datetime

    time_ranges = {'1 Minute': 30, '5 Minute': 150, '15 Minute': 2*60} # 2 hours for 15 min chart

    for timeframe, minutes in time_ranges.items():
        data = df if timeframe == '1 Minute' else df5 if timeframe == '5 Minute' else df15
        start_datetime, end_datetime = set_time_range(data, minutes)
        col = 5 if timeframe == '1 Minute' else 4 if timeframe == '5 Minute' else 3
        fig.update_xaxes(range=[start_datetime, end_datetime], row=1, col=col)
        fig.update_xaxes(range=[start_datetime, end_datetime], row=2, col=col)

    def set_dynamic_y_range(df, multiplier):
        low = df.tail(1).low.values[0]
        high = df.tail(1).high.values[0]
        ymin = math.ceil(low * (1 - multiplier))
        ymax = math.floor(high * (1 + multiplier))
        return ymin, ymax

    y_ranges = {'1 Minute': 0.02, '5 Minute': 0.02, '15 Minute': 0.05}
    for timeframe, multiplier in y_ranges.items():
        data = df if timeframe == '1 Minute' else df5 if timeframe == '5 Minute' else df15
        ymin, ymax = set_dynamic_y_range(data, multiplier)
        col = 5 if timeframe == '1 Minute' else 4 if timeframe == '5 Minute' else 3
        fig.update_yaxes(range=[ymin, ymax], row=1, col=col)


    fig.update_layout(title_text=Ticker, xaxis1_rangeslider_visible=True, xaxis2_rangeslider_visible=True,
                      xaxis_rangeslider_thickness=0.02,
                      height=1280, width=2500, showlegend=False)

    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')
    fig.update_traces(name=Ticker, selector=dict(type='candlestick'))

    config = {'scrollZoom': True}
    fig.show(config=config)


# Load data from JSON
def load_data_from_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Assuming your JSON structure allows direct conversion to DataFrame.  Adjust as needed.
    # Example: If your JSON has keys like "1min", "5min", etc.
    dfs = {}
    for key, value in data.items():
        try:
            df = pd.DataFrame(value)
            df.index = pd.to_datetime(df.index) # Crucial: Convert index to DateTimeIndex
            # Calculate indicators (SMAs, Bollinger Bands) -  Adapt for all dataframes
            df['SMA3'] = df['close'].rolling(window=3).mean()
            df['SMA14'] = df['close'].rolling(window=14).mean()
            df['SMA50'] = df['close'].rolling(window=50).mean()
            df['SMA200'] = df['close'].rolling(window=200).mean()
            df['BBL_14_2'] = df['close'] - 2*df['close'].rolling(window=14).std()
            df['BBU_14_2'] = df['close'] + 2*df['close'].rolling(window=14).std()

            dfs[key] = df
        except Exception as e:
            print(f"Error processing {key}: {e}")
            return None # Or handle the error as you see fit
    return dfs


# usage:
filepath = "data/fig_data.json"  # Path to your JSON file
loaded_data = load_data_from_json(filepath)

if loaded_data:
    df = loaded_data.get("1min")  # Access the DataFrames
    df5 = loaded_data.get("5min")
    df15 = loaded_data.get("15min")
    dfD = loaded_data.get("1day")  # Or however your daily data is keyed

    if all([df is not None, df5 is not None, df15 is not None, dfD is not None]):
        Ticker = "Ticker"  # Replace with your ticker
        Chart_Plot(Ticker, df, df5, df15, dfD)
    else:
        print("Error: Could not load all required dataframes from the JSON file.")
else:
    print("Failed to load data from JSON.")