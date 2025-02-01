import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time
import math
from datetime import datetime, timedelta
import webbrowser
import plotly
from plotly.io._base_renderers import BaseHTTPRequestHandler, HTTPServer
import plotly.offline as pyo
import uuid


#*************************************************************
def Chart_Plot_Std(Ticker, df, df5, df15, dfD):

    # Create subplots
    fig = make_subplots(rows=2, cols=4, subplot_titles=[ '1 Day', '15 Minute', '5 Minute', '1 Minute',
                         '', '', '', ''],
                        row_width=[0.15, 0.65], shared_yaxes=False, vertical_spacing=0.17,
                        horizontal_spacing=0.02, print_grid=False, )
    #pyo.plot(fig, filename='your_plot.html', auto_open=False)

    # Add 1M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close ), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1,  col=4)
    fig.add_trace( go.Scatter(x=df.index, y=df.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2), row=1, col=4)
    fig.add_trace( go.Scatter(x=df.index, y=df.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')), row=1,col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')), row=1,col=4)
    fig.update_xaxes(title_text="Slider - 1 Minute Time Interval", row=1, col=5)

    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df.index, y=df.volume, marker=dict(color='#7cadf8')), row=2, col=4)


    # Add 5M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df5.index, open=df5.open, high=df5.high, low=df5.low,close=df5.close ), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1,col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=3)
    fig.add_trace( go.Scatter(x=df5.index, y=df5.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2), row=1, col=3)
    fig.add_trace( go.Scatter(x=df5.index, y=df5.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')), row=1,  col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')), row=1, col=3)
    fig.update_xaxes(title_text="Slider - 5 Minute Time Interval", row=1, col=4)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df5.index, y=df5.volume, marker=dict(color='#7cadf8')), row=2, col=3)

    # Add 15M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df15.index, open=df15.open, high=df15.high, low=df15.low, close=df15.close ), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1,col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=2)
    fig.add_trace( go.Scatter(x=df15.index, y=df15.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2),  row=1, col=2)
    fig.add_trace( go.Scatter(x=df15.index, y=df15.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')), row=1,  col=2)
    fig.update_xaxes(title_text="Slider - 15 Minute Time Interval", row=1, col=3)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df15.index, y=df15.volume, marker=dict(color='#7cadf8')), row=2, col=2)

    # Add Day Candlestick Chart
    fig.add_trace(go.Candlestick(x=dfD.index, open=dfD.open, high=dfD.high, low=dfD.low, close=dfD.close),row=1, col=1)
    fig.add_trace(go.Scatter(x=dfD.index, y=dfD.SMA3_1D, mode='lines', name='SMA3_1D', line_color='#ff00ff'), row=1, col=1)
    fig.update_xaxes(title_text="Slider - 1 Day Time Interval", row=1, col=1)
    fig.update_xaxes(rangeslider_thickness=0.02)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=dfD.index, y=dfD.volume, marker=dict(color='#7cadf8')), row=2, col=1)

    # 1 Min Update the time selected zoom
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=1)                      #inset right side by 1 ticks
    formatted_new_time = new_time.strftime("%H:%M")                     #right side of graph is current time
    end_time_1 = datetime.strptime(formatted_new_time, '%H:%M')
    new_time = current_time - timedelta(minutes=30)                     # set range for plot
    formatted_new_time = new_time.strftime("%H:%M")
    start_time_1 = datetime.strptime(formatted_new_time, '%H:%M')
    last_day = df.index[-1].date()
    start_datetime_1 = datetime.combine(last_day, start_time_1.time())
    end_datetime_1 = datetime.combine(last_day, end_time_1.time())

    # 5 Min Update the time selected zoom to last day view
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=5)                     # inset right side by 1 ticks
    formatted_new_time = new_time.strftime("%H:%M")
    end_time_5 = datetime.strptime(formatted_new_time, '%H:%M')
    new_time = current_time - timedelta(minutes=150)                    # set range for plot
    formatted_new_time = new_time.strftime("%H:%M")
    start_time_5 = datetime.strptime(formatted_new_time, '%H:%M')
    last_day = df.index[-1].date()
    start_datetime_5 = datetime.combine(last_day, start_time_5.time())
    end_datetime_5 = datetime.combine(last_day, end_time_5.time())

    # 15 Min Update the time selected zoom to last day view
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=15)                     # inset right side by 1 ticks
    formatted_new_time = new_time.strftime("%H:%M")
    end_time_15 = datetime.strptime(formatted_new_time, '%H:%M')
    #new_time = current_time - timedelta(minutes=450)                    # set range for plot
    new_time = time(2,0) # set range for plot
    formatted_new_time = new_time.strftime("%H:%M")
    start_time_15 = datetime.strptime(formatted_new_time, '%H:%M')
    last_day = df.index[-1].date()
    start_datetime_15 = datetime.combine(last_day, start_time_15.time())
    end_datetime_15 = datetime.combine(last_day, end_time_15.time())

    # Set the x-axis range for each subplot
    fig.update_xaxes(range=[start_datetime_1, end_datetime_1], row=1, col=4)    # 1 min chart
    fig.update_xaxes(range=[start_datetime_1, end_datetime_1], row=2, col=4)    # 1 min chart volume
    fig.update_xaxes(range=[start_datetime_5, end_datetime_5], row=1, col=3)    # 5 min chart
    fig.update_xaxes(range=[start_datetime_5, end_datetime_5], row=2, col=3)    # 5 min chart volume
    fig.update_xaxes(range=[start_datetime_15, end_datetime_15], row=1, col=2)  # 15 min chart
    fig.update_xaxes(range=[start_datetime_15, end_datetime_15], row=2, col=2)  # 15 min chart volume

    # fig.update_xaxes(range=[start_datetime, end_datetime], row=1, col=2)      # day - full scale default

    filtered_df_1min = df.loc[start_time_1:end_time_1]
    #Dyn_Ymin = math.floor(filtered_df_1min['low'].min() * 1)
    #Dyn_Ymax = math.ceil(filtered_df_1min['high'].max() * 1)
    Dyn_Ymin = filtered_df_1min['low'].min()
    Dyn_Ymax = filtered_df_1min['high'].max()

    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=2, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=3, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=4, dtick=1)

    fig.update_yaxes(color='#000000', range=[0, 6000000], row=2, col=2)
    fig.update_yaxes(color='#000000', range=[0, 2000000], row=2, col=3)
    fig.update_yaxes(color='#000000', range=[0, 500000], row=2, col=4)

    fig.update_xaxes(gridcolor='lightgrey', row=1, col=1, dtick=24 * 60 * 60 * 1000, tickformat='%m-%d %H:%M')    # 1 Day graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=2, dtick=15 * 60 * 1000, tickformat='%m-%d %H:%M')         #15 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=3, dtick=5 * 60 * 1000, tickformat='%m-%d %H:%M')          #5 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=4, dtick=1 * 60 * 1000, tickformat='%m-%d %H:%M')          #1 min graph ticks

    '''
    #New Test
    fig_json = pio.to_json(fig)
    # Option 2: Store in a file
    with open("fig_data.json", "w") as f:
        f.write(fig_json)
    '''

    # Update traces name in legend (if on)
    fig.update_traces(name=Ticker, selector=dict(type='candlestick'))

    fig.update_layout(title_text=Ticker, xaxis1_rangeslider_visible=True, xaxis2_rangeslider_visible=True,
                      xaxis_rangeslider_thickness=0.02,
                      height=1280, width=2500, showlegend=False)
    fig.update_layout(yaxis=dict(tickmode= 'linear', tick0= Dyn_Ymin, dtick = 1))
    #fig.update_layout(xaxis=dict(tickmode='linear', tick0=0.25, dtick=1))

    # Prototype - Add Special lines, trends, key levels, BUY indications etc.
    '''
    fig.update_layout(
        title='NVDA Analysis',
        yaxis_title='NVDA Price [USD]',
        shapes=[dict(
            x0='2023-12-22 10:00:00', x1='2023-12-22 10:00:00', y0=0.0, y1=1, xref='x', yref='paper',
            line_width=1)],
        annotations=[dict(
            x='2023-12-22 10:00:00', y=0.0, xref='x', yref='paper',
            showarrow=False, xanchor='left', text='Buy')],
        showlegend=False  # Hide legend for better visualization
    )
    '''
    config = {'scrollZoom': True}
    fig.show(config=config)


#*************************************************************
def Chart_Plot_HistoAnalysis(Ticker, HistBeginDateTime, HistEndDateTime, df, df5, df15, dfD):
    global fig

    # Create subplots
    fig = make_subplots(rows=2, cols=4, subplot_titles=[ '1 Day', '15 Minute', '5 Minute', '1 Minute',
                        '', '', '', ''], row_width=[0.15, 0.65], shared_yaxes=False, vertical_spacing=0.17,
                        horizontal_spacing=0.02, print_grid=False, )
    #pyo.plot(fig, filename='your_plot.html',  auto_open=False)

    # Add 1M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2),
                  row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3),
                  row=1, col=4)
    fig.add_trace(
        go.Scatter(x=df.index, y=df.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=4)
    fig.add_trace(
        go.Scatter(x=df.index, y=df.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=4)
    fig.update_xaxes(title_text="Slider - 1 Minute Time Interval", row=1, col=4)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df.index, y=df.volume, marker=dict(color='#7cadf8')), row=2, col=4)

    # Add 5M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df5.index, open=df5.open, high=df5.high, low=df5.low, close=df5.close), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2),
        row=1, col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1,
        col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=3)
    fig.update_xaxes(title_text="Slider - 5 Minute Time Interval", row=1, col=3)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df5.index, y=df5.volume, marker=dict(color='#7cadf8')), row=2, col=3)

    # Add 15M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df15.index, open=df15.open, high=df15.high, low=df15.low, close=df15.close), row=1,
                  col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1,
                  col=2)
    fig.add_trace(
        go.Scatter(x=df15.index, y=df15.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2), row=1,
        col=2)
    fig.add_trace(
        go.Scatter(x=df15.index, y=df15.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1,
        col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBL_14_2, mode='lines', name='BBL_14_2',
                             line=dict(color='#56a6ae', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBU_14_2, mode='lines', name='BBU_14_2',
                             line=dict(color='#56a6ae', dash='dash')), row=1, col=2)
    fig.update_xaxes(title_text="Slider - 15 Minute Time Interval", row=1, col=2)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df15.index, y=df15.volume, marker=dict(color='#7cadf8')), row=2, col=2)

    # Add Day Candlestick Chart
    fig.add_trace(go.Candlestick(x=dfD.index, open=dfD.open, high=dfD.high, low=dfD.low, close=dfD.close), row=1, col=1)
    fig.add_trace(go.Scatter(x=dfD.index, y=dfD.SMA3_1D, mode='lines', name='SMA3_1D', line_color='#ff00ff'), row=1,
                  col=1)
    fig.update_xaxes(title_text="Slider - 1 Day Time Interval", row=1, col=1)
    fig.update_xaxes(rangeslider_thickness=0.02)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=dfD.index, y=dfD.volume, marker=dict(color='#7cadf8')), row=2, col=1)

    # Set the x-axis range for each subplot
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=4)  # 1 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=4)  # 1 min chart volume
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=3)  # 5 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=3)  # 5 min chart volume
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=2)  # 15 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=2)  # 15 min chart volume

    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=2)      # day - full scale default

    filtered_df_1min = df.loc[HistBeginDateTime:HistEndDateTime]

    Dyn_Ymin = math.floor(filtered_df_1min['low'].min() * 1)
    Dyn_Ymax = math.ceil(filtered_df_1min['high'].max() * 1)

    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=2, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=3, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=4, dtick=1)

    fig.update_yaxes(color='#000000', range=[0, 6000000], row=2, col=2)
    fig.update_yaxes(color='#000000', range=[0, 2000000], row=2, col=3)
    fig.update_yaxes(color='#000000', range=[0, 500000], row=2, col=4)

    fig.update_xaxes(gridcolor='lightgrey', row=1, col=1, dtick=24 * 60 * 60 * 1000, tickformat='%m-%d %H:%M')    # 1 Day graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=2, dtick = 15*60*1000, tickformat='%m-%d %H:%M')           # 15 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=3, dtick = 15*60*1000, tickformat='%m-%d %H:%M')           # 5 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=4, dtick= 15*60*1000, tickformat='%m-%d %H:%M')            # 1 min graph ticks


    # Update traces name in legend (if on)
    fig.update_traces(name=Ticker, selector=dict(type='candlestick'))

    fig.update_layout(title_text=Ticker, xaxis1_rangeslider_visible=True, xaxis2_rangeslider_visible=True,
                      xaxis_rangeslider_thickness=0.02, showlegend=False)
    fig.update_layout(yaxis=dict(tickmode='linear', tick0=Dyn_Ymin, dtick=1))


    # Prototype - Add Special lines, trends, key levels, BUY indications etc.
    '''
    fig.update_layout(
        title='NVDA Analysis',
        yaxis_title='NVDA Price [USD]',
        shapes=[dict(
            x0='2023-12-22 10:00:00', x1='2023-12-22 10:00:00', y0=0.0, y1=1, xref='x', yref='paper',
            line_width=1)],
        annotations=[dict(
            x='2023-12-22 10:00:00', y=0.0, xref='x', yref='paper',
            showarrow=False, xanchor='left', text='Buy')],
        showlegend=False  # Hide legend for better visualization
    )

    '''

    #config = {'scrollZoom': True}
    #fig.show(config=config)
    pyo.plot(fig, filename='DP_NVDA_PLOT.html', auto_open=True)



def Chart_Plot_Update(Ticker, HistBeginDateTime, HistEndDateTime, df, df5, df15, dfD):
    # Create subplots
    #fig = make_subplots(rows=2, cols=4, subplot_titles=[ '1 Day', '15 Minute', '5 Minute', '1 Minute',
    #                    '', '', '', ''], row_width=[0.1, 0.7], shared_yaxes=False, vertical_spacing=0.17,
    #                    horizontal_spacing=0.02, print_grid=False, )
    #pyo.plot(fig, filename='your_plot.html', auto_open=False)

    # Add 1M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2),
                  row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3),
                  row=1, col=4)
    fig.add_trace(
        go.Scatter(x=df.index, y=df.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=4)
    fig.add_trace(
        go.Scatter(x=df.index, y=df.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=4)
    fig.update_xaxes(title_text="Slider - 1 Minute Time Interval", row=1, col=4)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df.index, y=df.volume, marker=dict(color='#7cadf8')), row=2, col=4)

    # Add 5M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df5.index, open=df5.open, high=df5.high, low=df5.low, close=df5.close), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2),
        row=1, col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1,
        col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.BBL_14_2, mode='lines', name='BBL_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=3)
    fig.add_trace(
        go.Scatter(x=df5.index, y=df5.BBU_14_2, mode='lines', name='BBU_14_2', line=dict(color='#56a6ae', dash='dash')),
        row=1, col=3)
    fig.update_xaxes(title_text="Slider - 5 Minute Time Interval", row=1, col=3)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df5.index, y=df5.volume, marker=dict(color='#7cadf8')), row=2, col=3)

    # Add 15M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df15.index, open=df15.open, high=df15.high, low=df15.low, close=df15.close), row=1,
                  col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA3, mode='lines', name='SMA3', line_color='#ff00ff'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA14, mode='lines', name='SMA14', line_color='#ff0000'), row=1,
                  col=2)
    fig.add_trace(
        go.Scatter(x=df15.index, y=df15.SMA50, mode='lines', name='SMA50', line_color='#00ff00', line_width=2), row=1,
        col=2)
    fig.add_trace(
        go.Scatter(x=df15.index, y=df15.SMA200, mode='lines', name='SMA200', line_color='#0000ff', line_width=3), row=1,
        col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBL_14_2, mode='lines', name='BBL_14_2',
                             line=dict(color='#56a6ae', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBU_14_2, mode='lines', name='BBU_14_2',
                             line=dict(color='#56a6ae', dash='dash')), row=1, col=2)
    fig.update_xaxes(title_text="Slider - 15 Minute Time Interval", row=1, col=2)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df15.index, y=df15.volume, marker=dict(color='#7cadf8')), row=2, col=2)

    # Add Day Candlestick Chart
    fig.add_trace(go.Candlestick(x=dfD.index, open=dfD.open, high=dfD.high, low=dfD.low, close=dfD.close), row=1, col=1)
    fig.add_trace(go.Scatter(x=dfD.index, y=dfD.SMA3_1D, mode='lines', name='SMA3_1D', line_color='#ff00ff'), row=1,
                  col=1)
    fig.update_xaxes(title_text="Slider - 1 Day Time Interval", row=1, col=1)
    fig.update_xaxes(rangeslider_thickness=0.02)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=dfD.index, y=dfD.volume, marker=dict(color='#7cadf8')), row=2, col=1)

    # Set the x-axis range for each subplot
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=4)  # 1 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=4)  # 1 min chart volume
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=3)  # 5 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=3)  # 5 min chart volume
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=2)  # 15 min chart
    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=2, col=2)  # 15 min chart volume

    fig.update_xaxes(range=[HistBeginDateTime, HistEndDateTime], row=1, col=2)      # day - full scale default

    filtered_df_1min = df.loc[HistBeginDateTime:HistEndDateTime]

    Dyn_Ymin = math.floor(filtered_df_1min['low'].min() * 1)
    Dyn_Ymax = math.ceil(filtered_df_1min['high'].max() * 1)

    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=2, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=3, dtick=1)
    fig.update_yaxes(range=[Dyn_Ymin, Dyn_Ymax], row=1, col=4, dtick=1)

    fig.update_yaxes(color='#000000', range=[0, 6000000], row=2, col=2)
    fig.update_yaxes(color='#000000', range=[0, 2000000], row=2, col=3)
    fig.update_yaxes(color='#000000', range=[0, 300000], row=2, col=4)

    fig.update_xaxes(gridcolor='lightgrey', row=1, col=1, dtick=24 * 60 * 60 * 1000, tickformat='%m-%d %H:%M')    # 1 Day graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=2, dtick = 15*60*1000, tickformat='%m-%d %H:%M')           # 15 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=3, dtick = 15*60*1000, tickformat='%m-%d %H:%M')           # 5 min graph ticks
    fig.update_xaxes(gridcolor='lightgrey', row=1, col=4, dtick= 15*60*1000, tickformat='%m-%d %H:%M')            # 1 min graph ticks


    # Update traces name in legend (if on)
    fig.update_traces(name=Ticker, selector=dict(type='candlestick'))

    fig.update_layout(title_text=Ticker, xaxis1_rangeslider_visible=True, xaxis2_rangeslider_visible=True,
                      xaxis_rangeslider_thickness=0.02, showlegend=False)
    fig.update_layout(yaxis=dict(tickmode='linear', tick0=Dyn_Ymin, dtick=1))


    # Prototype - Add Special lines, trends, key levels, BUY indications etc.
    '''
    fig.update_layout(
        title='NVDA Analysis',
        yaxis_title='NVDA Price [USD]',
        shapes=[dict(
            x0='2023-12-22 10:00:00', x1='2023-12-22 10:00:00', y0=0.0, y1=1, xref='x', yref='paper',
            line_width=1)],
        annotations=[dict(
            x='2023-12-22 10:00:00', y=0.0, xref='x', yref='paper',
            showarrow=False, xanchor='left', text='Buy')],
        showlegend=False  # Hide legend for better visualization
    )

    '''

    pyo.plot(fig, filename='DP_NVDA_PLOT.html', auto_open=False)
    #config = {'scrollZoom': True}
    #fig.show(config=config)







#*************************************************************
def DebugPrints():

    if True:
        print('1 min bars ')
        value = stock_data_1.open()
        print(f"open: {value:.2f}")
        value = stock_data_1.high()
        print(f"high: {value:.2f}")
        value = stock_data_1.low()
        print(f"low: {value:.2f}")
        value = stock_data_1.close()
        print(f"close: {value:.2f}")
        value = stock_data_1.vwap()
        print(f"vwap: {value:.2f}")
        value = stock_data_1.volume()
        print(f"volume: {value:.2f}")
        value = stock_data_1.SMA3()
        print(f"SMA3: {value:.2f}")
        value = stock_data_1.SL_SMA3()
        print(f"SL_SMA3: {value:.2f}")
        value = stock_data_1.SMA14()
        print(f"SMA14: {value:.2f}")
        value = stock_data_1.SL_SMA14()
        print(f"SL_SMA14: {value:.2f}")

        print('5 min bars ')
        value = stock_data_5.open()
        print(f"open: {value:.2f}")
        value = stock_data_5.high()
        print(f"high: {value:.2f}")
        value = stock_data_5.low()
        print(f"low: {value:.2f}")
        value = stock_data_5.close()
        print(f"close: {value:.2f}")
        value = stock_data_5.vwap()
        print(f"vwap: {value:.2f}")
        value = stock_data_5.volume()
        print(f"volume: {value:.2f}")
        value = stock_data_5.SMA3()
        print(f"SMA3: {value:.2f}")
        value = stock_data_5.SL_SMA3()
        print(f"SL_SMA3: {value:.2f}")
        value = stock_data_5.SMA14()
        print(f"SMA14: {value:.2f}")
        value = stock_data_5.SL_SMA14()
        print(f"SL_SMA14: {value:.2f}")

        print('15 min bars ')
        value = stock_data_15.open()
        print(f"open: {value:.2f}")
        value = stock_data_15.high()
        print(f"high: {value:.2f}")
        value = stock_data_15.low()
        print(f"low: {value:.2f}")
        value = stock_data_15.close()
        print(f"close: {value:.2f}")
        value = stock_data_15.vwap()
        print(f"vwap: {value:.2f}")
        value = stock_data_15.volume()
        print(f"volume: {value:.2f}")
        value = stock_data_15.SMA3()
        print(f"SMA3: {value:.2f}")
        value = stock_data_15.SL_SMA3()
        print(f"SL_SMA3: {value:.2f}")
        value = stock_data_15.SMA14()
        print(f"SMA14: {value:.2f}")
        value = stock_data_15.SL_SMA14()
        print(f"SL_SMA14: {value:.2f}")

        print(' ')



