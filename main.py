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
TICKERS = ["NVDA", "MSFT", "AAPL", "GOOG", "TSLA", "AMZN", "META"]

# Timeframe options (including the new ones)
TIMEFRAMES = {
    "1 second": "second",
    "1 Min": "minute",
    "5 Min": "5min",  # Placeholder for aggregation
    "15 Min": "15min", # Placeholder for aggregation
    "1 Hour": "hour",
    "1 Week": "week",
    "1 Month": "month",
    "1 Quarter": "quarter",
    "1 Year": "year",
}

def fetch_stock_data(ticker, timeframe, polygon_client, candle_count=20):  # Added candle_count as a parameter
    """Fetch and aggregate stock data with dynamic date range and limited data points."""

    end_date = datetime.datetime.now(datetime.UTC)

    if timeframe in ["week", "month", "quarter", "year"]:
        if timeframe == "week":
            start_date = end_date - timedelta(days=365)
        elif timeframe == "month":
            start_date = end_date - timedelta(days=365 * 3)
        elif timeframe == "quarter":
            start_date = end_date - timedelta(days=365 * 5)
        elif timeframe == "year":
            start_date = end_date - timedelta(days=365 * 10)
    elif timeframe in ["second", "minute", "5min", "15min", "hour"]:
        if timeframe == "second":
            candle_count = 60 * 60
            lookback = timedelta(seconds=candle_count)
        elif timeframe == "minute":
            lookback = timedelta(minutes=candle_count)
        elif timeframe == "5min":
            lookback = timedelta(minutes=candle_count * 5)
        elif timeframe == "15min":
            lookback = timedelta(minutes=candle_count * 15)
        elif timeframe == "hour":
            lookback = timedelta(hours=candle_count)
        start_date = end_date - lookback
    else:
        start_date = end_date - timedelta(days=7)  # Default 7 days

    all_data = []
    current_date = start_date

    while current_date <= end_date:
        next_date = min(current_date + timedelta(days=365), end_date)  # Polygon API limit

        try:
            response = polygon_client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan="minute" if timeframe in ["5min", "15min"] or timeframe == "second" else timeframe,  # Fetch 1-min or 1-sec for aggregation
                from_=current_date.strftime("%Y-%m-%d"),
                to=next_date.strftime("%Y-%m-%d"),
                limit=5000  # Important: Limit for each request
            )

            if not response:
                print(f"⚠️ No data for {ticker} ({timeframe}) from {current_date} to {next_date}")
                current_date = next_date + timedelta(days=1)
                continue

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
            print(f"❌ Error fetching {ticker} ({timeframe}) from {current_date} to {next_date}: {e}")
            current_date = next_date + timedelta(days=1)
            continue

        current_date = next_date + timedelta(days=1)  # Move to the next day

    df = pd.DataFrame(all_data)

    if df.empty:
        print(f"⚠️ Empty DataFrame after pagination for {ticker} ({timeframe})")
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if timeframe == "5min":
        df = df.resample("5min", on='date').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        df = df.reset_index()
    elif timeframe == "15min":
        df = df.resample("15min", on='date').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        df = df.reset_index()
    elif timeframe == "second": # Added aggregation for second
        df = df.resample("1S", on='date').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        df = df.reset_index()

    if timeframe in ["second", "minute", "5min", "15min", "hour"]:
        if not df.empty:
            df = df.tail(candle_count)

    return df

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
DEFAULT_TIMEFRAME = "1 Hour"

# Dash App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Stock Analysis Dashboard"),

    # Ticker Dropdown with "Custom" option
    dcc.Dropdown(
        id="ticker-dropdown",
        options=[{"label": t, "value": t} for t in TICKERS] + [{"label": "Custom", "value": "custom"}],
        value=DEFAULT_TICKER
    ),

    # Ticker Input (hidden initially)
    dcc.Input(id="custom-ticker-input", type="text", placeholder="Enter ticker", style={"display": "none"}),

    # Charts Container
    html.Div(id="charts-container", style={"display": "flex", "flex-wrap": "wrap"}),  # Flexbox for layout

    # Error Message Display
    html.Div(id="error-message")
])
@app.callback(
    Output("custom-ticker-input", "style"),
    Input("ticker-dropdown", "value")
)
def toggle_ticker_input(selected_ticker):
    if selected_ticker == "custom":
        return {"display": "block"}
    else:
        return {"display": "none"}


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

                    fig.add_trace(go.Candlestick(
                        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick"
                    ))

                    for indicator in ["EMA_14", "EMA_50", "EMA_200", "BB_upper", "BB_lower"]:
                        if indicator in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df["date"], y=df[indicator], mode="lines", name=indicator
                            ))

                    fig.update_layout(
                        title=f"{ticker} Stock Analysis ({timeframe_label})",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )

                chart = html.Div(
                    dcc.Graph(id=f"stock-chart-{ticker}-{timeframe_value}", figure=fig),
                    style={
                        "width": "24%",  # 25% for 4 charts per row (adjust as needed)
                        "display": "inline-block",
                        "margin": "5px",  # Add some margin between charts
                    },
                )
                charts.append(chart)

        except Exception as e:
            print(f"Error for {timeframe_label}: {e}")
            error_message += f"An error occurred for {timeframe_label}: {e}. "
            fig = go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"Error: {timeframe_label}"))
            chart = html.Div(dcc.Graph(id=f"stock-chart-{ticker}-{timeframe_value}", figure=fig), style={"width": "24%", "display": "inline-block", "margin": "5px"})
            charts.append(chart)

    return charts, error_message

if __name__ == "__main__":
    app.run_server(debug=True)

