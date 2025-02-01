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

load_dotenv()

# Your Paid Polygon.io API Key
API_KEY = os.getenv("POLYGON_API_KEY")
polygon_client = RESTClient(API_KEY)

# Available stock tickers
TICKERS = ["NVDA", "MSFT", "AAPL", "GOOG", "TSLA", "AMZN", "META"]

# Timeframe options
TIMEFRAMES = {
    "1 Min": "minute",
    "5 Min": "minute",
    "15 Min": "minute",
    "1 Hour": "hour",
    "4 Hours": "hour",
    "1 Day": "day",
    "1 Week": "week",
}
def fetch_stock_data(ticker, timeframe):
    """ Fetch stock data from Polygon.io based on selected timeframe. """
    try:
        if timeframe is None:
            print(f"⚠️ No timeframe selected for {ticker}")
            return pd.DataFrame()
        
        end_date = datetime.datetime.now(datetime.UTC)
        start_date = end_date - timedelta(days=7)  # Fetch last 7 days

        response = polygon_client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan=timeframe,
            from_=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d"),
            limit=5000
        )

        # 🔹 Convert Agg objects to dictionary
        if not response:
            print(f"⚠️ No data received for {ticker} ({timeframe})")
            return pd.DataFrame()

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

        df = pd.DataFrame(data)
        print("stock data:", df.head())
        if df.empty:
            print(f"⚠️ Empty DataFrame for {ticker} ({timeframe})")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"❌ Error fetching {ticker} ({timeframe}): {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    """ Add EMA 14, EMA 50, EMA 200, and Bollinger Bands to the DataFrame. """
    if not df.empty:
        df["EMA_14"] = ta.ema(df["close"], length=14)
        df["EMA_50"] = ta.ema(df["close"], length=50)
        df["EMA_200"] = ta.ema(df["close"], length=200)
        
        bb = ta.bbands(df["close"], length=14, std=2)
        df["BB_upper"] = bb["BBU_14_2.0"]
        df["BB_lower"] = bb["BBL_14_2.0"]
    return df

# Dash App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Stock Analysis Dashboard"),
    
    dcc.Dropdown(id="ticker-dropdown", options=[{"label": t, "value": t} for t in TICKERS], value="NVDA"),
    
    dcc.Dropdown(id="timeframe-dropdown", options=[{"label": k, "value": v} for k, v in TIMEFRAMES.items()], value="1d"),
    
    dcc.Graph(id="stock-chart"),
])

@app.callback(
    Output("stock-chart", "figure"),
    [Input("ticker-dropdown", "value"), Input("timeframe-dropdown", "value")]
)
def update_chart(ticker, timeframe):
    df = fetch_stock_data(ticker, timeframe)
    print("calculate indicators:", df.head())
    df = calculate_indicators(df)
    print("calculated indicators:", df.head())
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick"
    ))
    
    # Moving Averages
    fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_14"], mode="lines", name="EMA 14"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_50"], mode="lines", name="EMA 50"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["EMA_200"], mode="lines", name="EMA 200"))
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df["date"], y=df["BB_upper"], mode="lines", name="Bollinger Upper", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df["date"], y=df["BB_lower"], mode="lines", name="Bollinger Lower", line=dict(dash="dot")))
    
    fig.update_layout(title=f"{ticker} Stock Analysis ({timeframe})", xaxis_title="Date", yaxis_title="Price")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
