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
from dash_extensions import WebSocket
import threading
import time

# Load environment variables
load_dotenv()

# Your Paid Polygon.io API Key
API_KEY = os.getenv("POLYGON_API_KEY")
polygon_client = RESTClient(API_KEY)

# Available stock tickers
TICKERS = ["NVDA", "SMCI", "TEM", "GOOG", "TSLA", "AMZN", "META", "ARM", "AVGO", "MRVL", "PLTR", "QCOM", "TSM", "ASML", "MU", "AAPL", "MSFT", "WMT", "RGTI", "QUBT", "SOUN"]

# Timeframe options
TIMEFRAMES = {
    "1 Sec": "1sec",
    "10 Sec": "10sec", 
    "1 Min": "minute",
    "5 Min": "5min",
    "15 Min": "15min",
    "1 Hour": "hour",
    "4 Hour": "4hour",
    "1 Day": "day",
    "1 Week": "week",
    "1 Month": "month",
    "1 Quarter": "quarter",
    "1 Year": "year"
}

# Default values
DEFAULT_TICKER = "NVDA"
DEFAULT_TIMEFRAME = "1 min"

# Helper function to fetch stock data
def fetch_stock_data(ticker, timeframe, polygon_client, candle_count=200):
    """Fetch and aggregate stock data with dynamic date range and limited data points."""
    end_date = datetime.datetime.now(datetime.UTC)

    base_timeframe_mapping = {
        "1sec": "second",
        "10sec": "second",
        "minute": "minute",
        "5min": "minute",
        "15min": "minute",
        "hour": "minute",
        "4hour": "hour",
        "day": "day",
        "week": "day",
        "month": "day",
        "quarter": "day",
        "year": "day"
    }

    lookback_multipliers = {
        "1sec": 1,
        "10sec": 10,
        "minute": 1,
        "5min": 5,
        "15min": 15,
        "hour": 60,
        "4hour": 240,
        "day": 1,
        "week": 7,
        "month": 30,
        "quarter": 90,
        "year": 365
    }

    base_timeframe = base_timeframe_mapping.get(timeframe, "minute")
    multiplier = lookback_multipliers.get(timeframe, 1)
    
    if base_timeframe == "second":
        lookback = timedelta(seconds=candle_count * multiplier * 2)
    elif base_timeframe == "minute":
        lookback = timedelta(minutes=candle_count * multiplier * 2)
    elif base_timeframe == "hour":
        lookback = timedelta(hours=candle_count * multiplier * 2)
    elif base_timeframe == "day":
        lookback = timedelta(days=candle_count * multiplier * 2)

    start_date = end_date - lookback

    unix_epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC)
    if start_date < unix_epoch:
        start_date = unix_epoch

    all_data = []
    current_date = start_date

    while current_date <= end_date:
        next_date = min(current_date + timedelta(days=365), end_date)

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

    df = pd.DataFrame(all_data)
    
    if df.empty:
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    resample_rules = {
        "1sec": '1s',
        "10sec": '10s',
        "minute": '1min',
        "5min": '5min',
        "15min": '15min',
        "hour": '1h',
        "4hour": '4h',
        "day": '1D',
        "week": '1W',
        "month": 'ME',
        "quarter": '3ME',
        "year": '1Y'
    }

    if timeframe in resample_rules:
        rule = resample_rules[timeframe]
        df = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

    df.reset_index(inplace=True)
    return df.tail(candle_count)

# Helper function to calculate indicators
def calculate_indicators(df):
    """Calculate indicators with improved error handling."""
    if df.empty:
        print("⚠️ DataFrame is empty. Cannot calculate indicators.")
        return df

    if df['close'].isnull().any():
        print("⚠️ NaN values found in 'close' column. Cannot calculate indicators.")
        print(df)
        return df

    try:
        df["EMA_14"] = ta.ema(df["close"], length=14)
        df["EMA_50"] = ta.ema(df["close"], length=50)
        df["EMA_200"] = ta.ema(df["close"], length=200)

        bb = ta.bbands(df["close"], length=14, std=2)

        if bb is None:
            print("⚠️ ta.bbands returned None. Cannot calculate Bollinger Bands.")
            return df

        df["BB_upper"] = bb["BBU_14_2.0"]
        df["BB_lower"] = bb["BBL_14_2.0"]

    except Exception as e:
        print(f"❌ Error calculating indicators: {e}")
    return df

# Dash App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H2("Stocks Dashboard"),

    dcc.Dropdown(
        id="ticker-dropdown",
        options=[{"label": t, "value": t} for t in TICKERS] + [{"label": "Custom", "value": "custom"}],
        value=DEFAULT_TICKER,
        style={
            "width": "30ch",
            "textAlign": "left",
            "display": "block",
        }
    ),

    dcc.Input(id="custom-ticker-input", type="text", placeholder="Enter ticker", style={"display": "none"}),

    WebSocket(id="ws", url="ws://127.0.0.1:5000/ws"),

    html.Div(id="charts-container", style={
        "display": "flex",
        "flex-wrap": "wrap",
        "width": "100%",
        "height": "80vh",
        "overflow-y": "auto",
    }),

    html.Div(id="error-message")
])

# Callback to toggle custom ticker input
@app.callback(
    Output("custom-ticker-input", "style"),
    Input("ticker-dropdown", "value")
)
def toggle_ticker_input(selected_ticker):
    if selected_ticker == "custom":
        return {"display": "block"}
    else:
        return {"display": "none"}

# Callback to update charts
@app.callback(
    Output("charts-container", "children"),
    Output("error-message", "children"),
    Input("ticker-dropdown", "value"),
    Input("custom-ticker-input", "value"),
    Input("ws", "message")  # Listen for WebSocket messages
)
def update_charts_container(selected_ticker, custom_ticker, ws_message):
    ticker = custom_ticker.upper() if selected_ticker == "custom" and custom_ticker else selected_ticker.upper() if selected_ticker != "custom" else DEFAULT_TICKER
    charts = []
    error_message = ""

    for timeframe_label, timeframe_value in TIMEFRAMES.items():
        try:
            df = fetch_stock_data(ticker, timeframe_value, polygon_client)

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

                    df["date"] = pd.to_datetime(df["date"])
                    df["date"] = df["date"] - pd.Timedelta(hours=7)

                    fig.add_trace(go.Candlestick(
                        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick", showlegend=False
                    ))

                    indicator_colors = {
                        "EMA_14": "red",
                        "EMA_50": "green",
                        "EMA_200": "blue",
                        "BB_upper": "grey",
                        "BB_lower": "grey"
                    }

                    line_style = {
                        "EMA_14": {"width": 1, "dash": "solid"},
                        "EMA_50": {"width": 2, "dash": "solid"},
                        "EMA_200": {"width": 3, "dash": "solid"},
                        "BB_upper": {"width": 1, "dash": "dash"},
                        "BB_lower": {"width": 1, "dash": "dash"}
                    }

                    for indicator in ["EMA_14", "EMA_50", "EMA_200", "BB_upper", "BB_lower"]:
                        if indicator in df.columns:
                            color = indicator_colors.get(indicator, "black")
                            line_properties = line_style.get(indicator, {"width": 1, "dash": "solid"})

                            fig.add_trace(go.Scatter(
                                x=df["date"], y=df[indicator], mode="lines", name=indicator, showlegend=False, 
                                line=dict(color=color, width=line_properties["width"], dash=line_properties["dash"])
                            ))

                    fig.add_trace(go.Scatter(
                        x=df["date"],
                        y=df["close"].rolling(window=2).mean(),
                        mode="lines",
                        name="Moving Average",
                        line=dict(color="mediumblue", width=1, dash="solid")
                    ))

                    volume_scaling_factor = 5
                    fig.add_trace(go.Bar(
                        x=df["date"], 
                        y=df["volume"] / volume_scaling_factor,
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
                        yaxis=dict(domain=[0.25, 1]),
                        yaxis2=dict(
                            title="Volume",
                            domain=[0, 0.2],
                            overlaying="y",
                            side="right",
                            showgrid=False
                        )
                    )

                chart = html.Div(
                    dcc.Graph(id=f"stock-chart-{ticker}-{timeframe_value}", figure=fig),
                    style={
                        "width": "24%",
                        "height": "50%",
                        "display": "inline-block",
                        "margin": "0px",
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

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)