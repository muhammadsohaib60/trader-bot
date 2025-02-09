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

# Updated timeframe configuration
TIMEFRAMES = {
    "1 Min": {"timespan": "minute", "multiplier": 1, "candles": 20, "days_back": 5},
    "5 Min": {"timespan": "minute", "multiplier": 5, "candles": 24, "days_back": 2},  # Show last 2 hours
    "15 Min": {"timespan": "minute", "multiplier": 15, "candles": 24, "days_back": 2},  # Show last 6 hours
    "1 Hour": {"timespan": "hour", "multiplier": 1, "candles": 24, "days_back": 2},  # 24 hours = 1 day
    "4 Hour": {"timespan": "hour", "multiplier": 4, "candles": 24, "days_back": 12},  # 24 candles = 4 days * 6 candles/day
    "1 Day": {"timespan": "day", "multiplier": 1, "candles": 20, "days_back": 30},
    "1 Week": {"timespan": "week", "multiplier": 1, "candles": 200, "days_back": 365},
    "1 Month": {"timespan": "month", "multiplier": 1, "candles": 200, "days_back": 730}
}

def fetch_stock_data(ticker, timeframe_config):
    """Fetch stock data without market hours filtering for hourly timeframes"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=timeframe_config["days_back"])
    
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

        # Convert timestamps to Eastern Time
        data = [{
            "date": pd.to_datetime(agg.timestamp, unit="ms", utc=True).tz_convert('US/Eastern').tz_localize(None),
            "open": agg.open,
            "high": agg.high,
            "low": agg.low,
            "close": agg.close,
            "volume": agg.volume,
            "vwap": getattr(agg, 'vwap', None)
        } for agg in response]

        df = pd.DataFrame(data).sort_values('date')
        
        # Filter only for minute timeframes
        if timeframe_config["timespan"] == "minute":
            df = df[df['date'].dt.time.between(datetime.strptime('09:30', '%H:%M').time(),
                                              datetime.strptime('16:00', '%H:%M').time())]
            df = df[df['date'].dt.dayofweek < 5]  # Filter weekdays

        # Get the latest required number of candles
        df = df.tail(timeframe_config["candles"])

        # Print debugging info for 4 Hour and 1 Day timeframes
        # if timeframe_config["timespan"] == "hour" and timeframe_config["multiplier"] == 1:
        #     print(f"1 Hour Data for {ticker}:\n{df}")
        # elif timeframe_config["timespan"] == "hour" and timeframe_config["multiplier"] == 4:
        #     print(f"4 Hour Data for {ticker}:\n{df}")
        # elif timeframe_config["timespan"] == "day":
        #     print(f"1 Day Data for {ticker}:\n{df.tail(30)}")

        
        return df

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def calculate_indicators(df):
    """Calculate technical indicators."""
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
    dcc.Dropdown(
        id="ticker-dropdown",
        options=[{"label": t, "value": t} for t in TICKERS] + [{"label": "Custom", "value": "custom"}],
        value="NVDA",
        style={"width": "30ch", "textAlign": "left", "display": "block"}
    ),
    dcc.Input(
        id="custom-ticker-input",
        type="text",
        placeholder="Enter ticker",
        style={"display": "none"}
    ),
    html.Div(id="charts-container", style={
        "display": "flex",
        "flex-wrap": "wrap",
        "width": "100%",
        "height": "100vh",
        "overflow-y": "auto",
    }),
    html.Div(id="error-message")
])

@app.callback(
    Output("charts-container", "children"),
    Output("error-message", "children"),
    Input("ticker-dropdown", "value"),
    Input("custom-ticker-input", "value")
)
def update_charts_container(selected_ticker, custom_ticker):
    ticker = custom_ticker.upper() if selected_ticker == "custom" and custom_ticker else selected_ticker.upper()
    charts = []
    error_message = ""

    for timeframe_label, timeframe_config in TIMEFRAMES.items():
        try:
            df = fetch_stock_data(ticker, timeframe_config)
            
            if df.empty:
                fig = go.Figure(layout=go.Layout(title=f"No data for {ticker} ({timeframe_label})"))
                error_message += f"No data found for {ticker} ({timeframe_label}). "
            else:
                df = calculate_indicators(df)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df["date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price",
                    showlegend=False
                ))
                # Add indicators
                indicator_styles = {
                    "EMA_14": {"color": "red", "width": 1, "dash": "solid"},
                    "EMA_50": {"color": "green", "width": 2, "dash": "solid"},
                    "EMA_200": {"color": "blue", "width": 3, "dash": "solid"},
                    "BB_upper": {"color": "grey", "width": 1, "dash": "dash"},
                    "BB_lower": {"color": "grey", "width": 1, "dash": "dash"}
                }

                for indicator, style in indicator_styles.items():
                    if indicator in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df["date"],
                            y=df[indicator],
                            mode="lines",
                            name=indicator,
                            line=style,
                            showlegend=False
                        ))

                # Volume bars
                fig.add_trace(go.Bar(
                    x=df["date"],
                    y=df["volume"],
                    name="Volume",
                    marker_color="blue",
                    opacity=0.2,
                    yaxis="y2",
                ))

                # Layout updates
                fig.update_layout(
                    title=f"{ticker} ({timeframe_label})",
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
                dcc.Graph(
                    id=f"stock-chart-{ticker}-{timeframe_config['timespan']}-{timeframe_config['multiplier']}",
                    figure=fig
                ),
                style={
                    "width": "24%",
                    "height": "50%",
                    "display": "inline-block",
                    "padding": "1px",
                    "margin": "1px"
                }
            )
            charts.append(chart)

        except Exception as e:
            print(f"Error for {timeframe_label}: {e}")
            error_message += f"Error in {timeframe_label}: {str(e)}. "

    return charts, error_message

if __name__ == "__main__":
    app.run_server(debug=True)