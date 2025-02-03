import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
#from polygon import RESTClient
from polygon.rest import RESTClient

from datetime import timedelta
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Your Paid Polygon.io API Key
API_KEY = os.getenv("EQkl8zAWXKa434UJKkhUjNChHpW3p9_a")
polygon_client = RESTClient(API_KEY)

# Available stock tickers
TICKERS = ["NVDA", "MSFT", "AAPL", "GOOG", "TSLA", "AMZN", "META"]

# Timeframe options
TIMEFRAMES = {
    "1 second": "second",
    "1 Min": "minute",
    "1 Hour": "hour",
    "1 Week": "week",
    "1 Month": "month",
    "1 Quarter": "quarter",
    "1 Year": "year",
}
import pandas as pd
from polygon import RESTClient
from datetime import timedelta
import datetime

def fetch_stock_data(ticker, timeframe, polygon_client):
    """Fetch stock data from Polygon.io with pagination."""

    end_date = datetime.datetime.now(datetime.UTC)
    start_date = end_date - timedelta(days=7)  # Initial range (adjust as needed)

    all_data = []
    current_date = start_date

    while current_date <= end_date:  # Changed to <= for inclusivity
        next_date = min(current_date + timedelta(days=365), end_date) # Polygon limit is around 1 year

        try:
            response = polygon_client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan=timeframe,
                from_=current_date.strftime("%Y-%m-%d"),
                to=next_date.strftime("%Y-%m-%d"),
                limit=5000  # Important: Keep the limit
            )

            if not response:
                print(f"⚠️ No data received for {ticker} ({timeframe}) from {current_date} to {next_date}")
                # Handle the case where no data is received for a specific date range.
                # You might want to continue to the next date range or break the loop.
                current_date = next_date + timedelta(days=1)
                continue # Skip to the next iteration.

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
            # Handle exceptions appropriately. You might want to retry the request,
            # skip to the next date range, or break the loop entirely.
            # Example: break # Stop fetching if there's an error.
            current_date = next_date + timedelta(days=1)
            continue # Skip to the next iteration.

        current_date = next_date + timedelta(days=1)

    df = pd.DataFrame(all_data)

    if df.empty:
        print(f"⚠️ Empty DataFrame after pagination for {ticker} ({timeframe})")
        return pd.DataFrame()

    # Ensure 'date' is datetime and other columns are numeric
    df['date'] = pd.to_datetime(df['date'])
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 'coerce' handles invalid values

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


# Dash App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Stock Analysis Dashboard"),
    
    dcc.Dropdown(id="ticker-dropdown", options=[{"label": t, "value": t} for t in TICKERS], value="NVDA"),
    
    dcc.Dropdown(id="timeframe-dropdown", options=[{"label": k, "value": v} for k, v in TIMEFRAMES.items()], value="day"), # Default to "day"
    
    dcc.Graph(id="stock-chart"),
])

@app.callback(
    Output("stock-chart", "figure"),
    [Input("ticker-dropdown", "value"), Input("timeframe-dropdown", "value")]
)
def update_chart(ticker, timeframe):
    global polygon_client

    df = fetch_stock_data(ticker, timeframe, polygon_client)

    if df.empty:
        return go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"No data for {ticker} ({timeframe})"))

    df = calculate_indicators(df)

    if df.empty: # Check again after indicator calculation
        return go.Figure(data=[go.Scatter(x=[], y=[])], layout=go.Layout(title=f"No data for {ticker} ({timeframe})"))

    fig = go.Figure()
    
    # Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick"
    ))
    
    # Moving Averages (only add if they exist in the DataFrame)
    if "EMA_14" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_14"], mode="lines", name="EMA 14"))
    if "EMA_50" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_50"], mode="lines", name="EMA 50"))
    if "EMA_200" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_200"], mode="lines", name="EMA 200"))
    
    # Bollinger Bands (only add if they exist)
    if "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["BB_upper"], mode="lines", name="Bollinger Upper", line=dict(dash="dot")))
    if "BB_lower" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["BB_lower"], mode="lines", name="Bollinger Lower", line=dict(dash="dot")))
    
    fig.update_layout(title=f"{ticker} Stock Analysis ({timeframe})", xaxis_title="Date", yaxis_title="Price")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)