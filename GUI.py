import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from polygon import RESTClient
from datetime import date, timedelta

# Your Polygon.io API key - **REPLACE with your actual key**
API_KEY = "YOUR_API_KEY"  
polygon_client = RESTClient(API_KEY)

# Stock tickers to analyze
TICKERS = ["NVDA", "MSFT", "AAPL", "GOOG", "TSLA", "AMZN", "META"]

def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo", interval="1d")
        df = df.reset_index()
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def preprocess_data(df):
    if not df.empty:
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["rsi"] = ta.rsi(df["close"], length=14)
        return df
    return pd.DataFrame()

# Dash App
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(id="ticker-dropdown", options=[{"label": t, "value": t} for t in TICKERS], value="NVDA"),
    dcc.Graph(id="stock-chart")
])

@app.callback(
    Output("stock-chart", "figure"),
    [Input("ticker-dropdown", "value")]
)
def update_chart(ticker):
    df = fetch_stock_data(ticker)
    df = preprocess_data(df)
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candlestick"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], mode="lines", name="SMA 20"))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
