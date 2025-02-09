import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from polygon import RESTClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("POLYGON_API_KEY")
polygon_client = RESTClient(API_KEY)

TICKERS = ["NVDA", "SMCI", "TEM", "GOOG", "TSLA", "AMZN", "META", "ARM", "AVGO", "MRVL", "PLTR", "QCOM", "TSM", "ASML", "MU", "AAPL", "MSFT", "WMT", "RGTI", "QUBT", "SOUN"]

TIMEFRAMES = {
    "1 Min": {"timespan": "minute", "multiplier": 1, "candles": 20},
    "5 Min": {"timespan": "minute", "multiplier": 5, "candles": 20},
    "15 Min": {"timespan": "minute", "multiplier": 15, "candles": 20},
    "1 Hour": {"timespan": "hour", "multiplier": 1, "candles": 20},
    "4 Hour": {"timespan": "hour", "multiplier": 4, "candles": 20},
    "1 Day": {"timespan": "day", "multiplier": 1, "candles": 20},
    "1 Week": {"timespan": "week", "multiplier": 1, "candles": 20},
    "1 Month": {"timespan": "month", "multiplier": 1, "candles": 20}
}

def fetch_stock_data(ticker, timeframe_config):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)  # Ensure enough data is retrieved
    
    try:
        response = polygon_client.get_aggs(
            ticker=ticker,
            multiplier=timeframe_config["multiplier"],
            timespan=timeframe_config["timespan"],
            from_=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d"),
            limit=50000
        )

        if not response:
            return pd.DataFrame()

        data = [{
            "date": pd.to_datetime(agg.timestamp, unit="ms", utc=True).tz_convert('US/Eastern').tz_localize(None),
            "open": agg.open,
            "high": agg.high,
            "low": agg.low,
            "close": agg.close,
            "volume": agg.volume,
            "vwap": getattr(agg, 'vwap', None)
        } for agg in response]

        df = pd.DataFrame(data).sort_values('date').tail(timeframe_config["candles"])
        return df
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def calculate_indicators(df):
    if df.empty:
        return df
    try:
        df["EMA_14"] = ta.ema(df["close"], length=14)
        df["EMA_50"] = ta.ema(df["close"], length=50)
        df["EMA_200"] = ta.ema(df["close"], length=200)
        bb = ta.bbands(df["close"], length=14, std=2)
        if bb is not None:
            df["BB_upper"] = bb["BBU_14_2.0"]
            df["BB_lower"] = bb["BBL_14_2.0"]
    except Exception as e:
        print(f"Error calculating indicators: {e}")
    return df

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H2("Stocks Dashboard"),
    dcc.Dropdown(id="ticker-dropdown", options=[{"label": t, "value": t} for t in TICKERS] + [{"label": "Custom", "value": "custom"}], value="NVDA"),
    dcc.Input(id="custom-ticker-input", type="text", placeholder="Enter ticker", style={"display": "none"}),
    html.Div(id="charts-container"),
    html.Div(id="error-message")
])

@app.callback(
    [Output("charts-container", "children"), Output("error-message", "children")],
    [Input("ticker-dropdown", "value"), Input("custom-ticker-input", "value")]
)
def update_charts_container(selected_ticker, custom_ticker):
    ticker = custom_ticker.upper() if selected_ticker == "custom" and custom_ticker else selected_ticker.upper()
    charts = []
    error_message = ""
    
    for timeframe_label, timeframe_config in TIMEFRAMES.items():
        try:
            df = fetch_stock_data(ticker, timeframe_config)
            if df.empty:
                error_message += f"No data found for {ticker} ({timeframe_label}). "
                continue
            df = calculate_indicators(df)
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"]))
            for col, style in {"EMA_14": "red", "EMA_50": "green", "EMA_200": "blue", "BB_upper": "grey", "BB_lower": "grey"}.items():
                if col in df.columns:
                    fig.add_trace(go.Scatter(x=df["date"], y=df[col], mode="lines", line=dict(color=style)))
            fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color="blue", opacity=0.2, yaxis="y2"))
            fig.update_layout(title=f"{ticker} ({timeframe_label})", xaxis_rangeslider_visible=False, yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False), showlegend=False)
            charts.append(html.Div(dcc.Graph(figure=fig), style={"width": "24%", "display": "inline-block"}))
        except Exception as e:
            error_message += f"Error in {timeframe_label}: {str(e)}. "
    return charts, error_message

if __name__ == "__main__":
    app.run_server(debug=True)
