import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from polygon import RESTClient
from datetime import timedelta
import datetime
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()

# Your Paid Polygon.io API Key
API_KEY = os.getenv("POLYGON_API_KEY")
polygon_client = RESTClient(API_KEY)

# Available stock tickers
TICKERS = ["NVDA", "SMCI", "TEM", "GOOG", "TSLA", "AMZN", "META", "ARM", "AVGO", "MRVL", "PLTR", "QCOM", "TSM", "ASML", "MU", "AAPL", "MSFT", "WMT", "RGTI", "QUBT", "SOUN"]

# Timeframe options (only the specified timeframes)
TIMEFRAMES = {
    "1 Min": "1min",
    "5 Min": "5min",
    "15 Min": "15min",
    "1 Hour": "1hour",
    "4 Hour": "4hour",
    "1 Day": "1day",
    "1 Week": "1week",
    "1 Month": "1month"
}

# Update the fetch_stock_data function to handle the new timeframes
def fetch_stock_data(ticker, timeframe, polygon_client, candle_count=200):
    """Fetch and aggregate stock data from minute-level data."""
    end_date = datetime.datetime.now(datetime.UTC)
    
    # Map timeframes to appropriate base timeframe for fetching
    timeframe_mapping = {
        "1min": ("minute", 1),
        "5min": ("minute", 5),
        "15min": ("minute", 15),
        "1hour": ("minute", 60),
        "4hour": ("minute", 240),
        "1day": ("day", 1),
        "1week": ("day", 7),
        "1month": ("day", 30)
    }
    
    base_timeframe, multiplier = timeframe_mapping.get(timeframe, ("minute", 1))
    
    # Calculate lookback period
    if base_timeframe == "minute":
        lookback = timedelta(days=5)  # Get 5 days of minute data for intraday timeframes
    else:
        lookback = timedelta(days=365)  # Get 1 year of daily data for larger timeframes
        
    start_date = end_date - lookback

    all_data = []
    current_date = start_date

    while current_date <= end_date:
        next_date = min(current_date + timedelta(days=5), end_date)
        
        try:
            response = polygon_client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan=base_timeframe,
                from_=current_date.strftime("%Y-%m-%d"),
                to=next_date.strftime("%Y-%m-%d"),
                limit=50000
            )

            if response:
                data = [
                    {
                        "date": pd.to_datetime(agg.timestamp, unit="ms"),
                        "open": agg.open,
                        "high": agg.high,
                        "low": agg.low,
                        "close": agg.close,
                        "volume": agg.volume
                    }
                    for agg in response
                ]
                all_data.extend(data)

        except Exception as e:
            print(f"Error fetching data: {e}")

        current_date = next_date + timedelta(days=1)

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Resample data based on timeframe
    resample_rules = {
        "1min": '1T',
        "5min": '5T',
        "15min": '15T',
        "1hour": '1H',
        "4hour": '4H',
        "1day": '1D',
        "1week": '1W',
        "1month": '1M'
    }

    if timeframe in resample_rules:
        rule = resample_rules[timeframe]
        df = df.resample(rule, closed='left', label='left').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

    df.reset_index(inplace=True)
    
    # Ensure we're working with current timezone
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    
    # Return only the most recent candles
    return df.tail(candle_count)

#*********************************
def calculate_indicators(df):
    """Calculate indicators with improved error handling."""
    if df.empty:
        print("⚠️ DataFrame is empty. Cannot calculate indicators.")
        return df  # Return the empty DataFrame

    # Check for NaNs in 'close' before calculating indicators
    if df['close'].isnull().any():
        print("⚠️ NaN values found in 'close' column. Cannot calculate indicators.")
        print(df) # Print the df to see where are the NaN values
        return df  # Return the DataFrame without indicator calculation

    try:
        df["EMA_14"] = ta.ema(df["close"], length=14)
        df["EMA_50"] = ta.ema(df["close"], length=50)
        df["EMA_200"] = ta.ema(df["close"], length=200)

        bb = ta.bbands(df["close"], length=14, std=2)

        if bb is None: # Check if bb is None
            print("⚠️ ta.bbands returned None. Cannot calculate Bollinger Bands.")
            return df # Return the DataFrame without BB calculation

        df["BB_upper"] = bb["BBU_14_2.0"]
        df["BB_lower"] = bb["BBL_14_2.0"]

    except Exception as e:
        print(f"❌ Error calculating indicators: {e}")
    return df


# Default values
DEFAULT_TICKER = "NVDA"  # Or any ticker you prefer
DEFAULT_TIMEFRAME = "1 min"

# *******************************************************************************************************
# Dash App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Update the app layout to display 8 charts (2 rows of 4 charts each)
app.layout = html.Div([
    html.H2("Stocks Dashboard"),

    # Ticker Dropdown with "Custom" option
    dcc.Dropdown(
        id="ticker-dropdown",
        options=[{"label": t, "value": t} for t in TICKERS] + [{"label": "Custom", "value": "custom"}],
        value=DEFAULT_TICKER,
        style={
            "width": "30ch",  # Limits width to approximately 30 characters
            "textAlign": "left",  # Left-aligns text
            "display": "block",  # Ensures it aligns properly in a column layout
        }
    ),

    # Ticker Input (hidden initially)
    dcc.Input(id="custom-ticker-input", type="text", placeholder="Enter ticker", style={"display": "none"}),

    # Charts Container (main web page window)
    html.Div(id="charts-container", style={
        "display": "flex",
        "flex-wrap": "wrap",
        "width": "100%",
        "height": "100vh",  # Set a maximum height for the chart container (adjust as needed)
        "overflow-y": "auto",  # Add a scrollbar if content exceeds height
    }),  # Flexbox for layout

    # Error Message Display
    html.Div(id="error-message")
])

# Update the chart container callback to display 8 charts
@app.callback(
    Output("charts-container", "children"),
    Output("error-message", "children"),
    Input("ticker-dropdown", "value"),
    Input("custom-ticker-input", "value")
)
def update_charts_container(selected_ticker, custom_ticker):
    ticker = custom_ticker.upper() if selected_ticker == "custom" and custom_ticker else selected_ticker.upper() if selected_ticker != "custom" else DEFAULT_TICKER
    charts = []
    error_message = ""

    for timeframe_label, timeframe_value in TIMEFRAMES.items():
        try:
            df = fetch_stock_data(ticker, timeframe_value, polygon_client)
            print(f"Data for {timeframe_label}:")
            print(df.head(2))

            if df.empty:
                fig = go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"No data for {ticker} ({timeframe_label})"))
                error_message += f"No data found for {ticker} with the selected timeframe. "
            else:
                df = calculate_indicators(df)

                if df.empty:
                    fig = go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"Error calculating indicators for {ticker}"))
                    error_message += f"Error calculating indicators for {ticker}. "
                else:
                    fig = go.Figure()
                    df = df.tail(30)

                    df["date"] = pd.to_datetime(df["date"])  # Ensure it's in datetime format
                    df["date"] = df["date"] - pd.Timedelta(hours=7)  # Subtract 7 hours
                    print(f"Adjusted date for {timeframe_label}:")
                    print(df["date"].head(2))

                    fig.add_trace(go.Candlestick(
                        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick", showlegend=False
                    ))

                    # Define a color map for each indicator
                    indicator_colors = {
                        "EMA_14": "red",
                        "EMA_50": "green",
                        "EMA_200": "blue",
                        "BB_upper": "grey",
                        "BB_lower": "grey"
                        }
                    # Define line weight and style (e.g., width and dash type)
                    line_style = {
                        "EMA_14": {"width": 1, "dash": "solid"},
                        "EMA_50": {"width": 2, "dash": "solid"},
                        "EMA_200": {"width": 3, "dash": "solid"},
                        "BB_upper": {"width": 1, "dash": "dash"},
                        "BB_lower": {"width": 1, "dash": "dash"}
                    }

                    for indicator in ["EMA_14", "EMA_50", "EMA_200", "BB_upper", "BB_lower"]:
                        if indicator in df.columns:
                            color = indicator_colors.get(indicator, "black")  # Default to black 
                            line_properties = line_style.get(indicator, {"width": 1, "dash": "solid"})  # Default style

                            fig.add_trace(go.Scatter(
                                x=df["date"], y=df[indicator], mode="lines", name=indicator, showlegend=False, 
                                line=dict(color=color,
                                width=line_properties["width"],  # Set the line width
                                dash=line_properties["dash"]     # Set the line style (solid, dash, dot) 
                                )
                            ))

                    fig.add_trace(go.Scatter(
                        x=df["date"],
                        y=df["close"].rolling(window=2).mean(),
                        mode="lines",
                        name="Moving Average",
                        line=dict(color="mediumblue", width=1, dash="solid")
                    ))

                    # Add volume trace as a bar chart
                    volume_scaling_factor = 5  # Adjust this value to control the height of the volume bars
                    fig.add_trace(go.Bar(
                        x=df["date"], 
                        y=df["volume"] / volume_scaling_factor,  # Scale down the volume values
                        name="Volume", 
                        marker_color="blue", 
                        opacity=0.07, 
                        yaxis="y2"
                    ))

                    fig.update_layout(
                        title=f"{ticker}  ({timeframe_label})",  
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=640,
                        showlegend=False,                    
                        xaxis_rangeslider_visible=False,      
                        xaxis=dict(domain=[0, 1]),
                        
                        # Primary Y-axis (Price)
                        yaxis=dict(
                            domain=[0.25, 1]  # Candlestick chart takes 75% of the space (from 25% to 100%)
                        ),

                        # Secondary Y-axis (Volume)
                        yaxis2=dict(
                            title="Volume",
                            domain=[0, 0.2],  # Volume chart takes 20% of the space (from 0% to 20%)
                            overlaying="y",
                            side="right",
                            showgrid=False
                        )
                    )

                chart = html.Div(
                    dcc.Graph(id=f"stock-chart-{ticker}-{timeframe_value}", figure=fig),
                    style={
                        "width": "24%",  # 25% for 4 charts per row (adjust as needed)
                        "height": "50%",
                        "display": "inline-block",
                        "margin": "0px",  # Add some margin between charts
                        "justify-content": "space-evenly", 
                        "align-items": "baseline", 
                        "gap": "1px", 
                        "padding": "1px", 
                        "margin": "1px", 
                    },
                )
                charts.append(chart)

        except Exception as e:
            print(f"Error for {timeframe_label}: {e}")
            error_message += f"An error occurred for {timeframe_label}: {e}. "
            fig = go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"Error: {timeframe_label}"))
            chart = html.Div(dcc.Graph(id=f"stock-chart-{ticker}-{timeframe_value}", figure=fig), style={"width": "24.8%", "display": "inline-block", "margin": "1px"})
            charts.append(chart)

    return charts, error_message
if __name__ == "__main__":
    app.run_server(debug=True)