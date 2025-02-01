import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time
import math






def Chart_Plot(Ticker, df, df5, df15, dfD):

    # Create subplots
    fig = make_subplots(rows=2, cols=5, subplot_titles=['CONTROLS:', '1 Day', '15 Minute', '5 Minute', '1 Minute', ' ', '1 Day Volume', '15 Min Volume',
                        '5 Min Volume', '1 Min Volume'], row_width=[0.2, 0.7], shared_yaxes=False, vertical_spacing=0.15, horizontal_spacing=0.02, print_grid=True, )


    # Add 1M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close ), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA3_1M, mode='lines', name='SMA3_1M', line_color='#ff00ff'), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA14_1M, mode='lines', name='SMA14_1M', line_color='#ff0000'), row=1,  col=5)
    fig.add_trace( go.Scatter(x=df.index, y=df.SMA50_1M, mode='lines', name='SMA50_1M', line_color='#00ff00', line_width=2), row=1, col=5)
    fig.add_trace( go.Scatter(x=df.index, y=df.SMA200_1M, mode='lines', name='SMA200_1M', line_color='#0000ff', line_width=3), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=df.BBL1_14_2, mode='lines', name='BBL_14_2_1M', line=dict(color='#56a6ae', dash='dash')), row=1,col=5)
    fig.add_trace(go.Scatter(x=df.index, y=df.BBU1_14_2, mode='lines', name='BBU_14_2_1M', line=dict(color='#56a6ae', dash='dash')), row=1,col=5)
    fig.update_xaxes(title_text="Slider - 1 Minute Time Interval", row=1, col=5)

    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df.index, y=df.volume, marker=dict(color='#7cadf8')), row=2, col=5)


    # Add 5M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df5.index, open=df5.open, high=df5.high, low=df5.low,close=df5.close ), row=1, col=4)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA3_5M, mode='lines', name='SMA5_1M', line_color='#ff00ff'), row=1,col=4)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.SMA14_5M, mode='lines', name='SMA14_5M', line_color='#ff0000'), row=1, col=4)
    fig.add_trace( go.Scatter(x=df5.index, y=df5.SMA50_5M, mode='lines', name='SMA50_5M', line_color='#00ff00', line_width=2), row=1, col=4)
    fig.add_trace( go.Scatter(x=df5.index, y=df5.SMA200_5M, mode='lines', name='SMA200_5M', line_color='#0000ff', line_width=3), row=1, col=4)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.BBL5_14_2, mode='lines', name='BBL_14_2_5M', line=dict(color='#56a6ae', dash='dash')), row=1,  col=4)
    fig.add_trace(go.Scatter(x=df5.index, y=df5.BBU5_14_2, mode='lines', name='BBU_14_2_5M', line=dict(color='#56a6ae', dash='dash')), row=1, col=4)
    fig.update_xaxes(title_text="Slider - 5 Minute Time Interval", row=1, col=4)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df5.index, y=df5.volume, marker=dict(color='#7cadf8')), row=2, col=4)

    # Add 15M Candlestick Chart
    fig.add_trace(go.Candlestick(x=df15.index, open=df15.open, high=df15.high, low=df15.low, close=df15.close ), row=1, col=3)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA3_15M, mode='lines', name='SMA3_15M', line_color='#ff00ff'), row=1,col=3)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.SMA14_15M, mode='lines', name='SMA14_15M', line_color='#ff0000'), row=1, col=3)
    fig.add_trace( go.Scatter(x=df15.index, y=df15.SMA50_15M, mode='lines', name='SMA50_15M', line_color='#00ff00', line_width=2),  row=1, col=3)
    fig.add_trace( go.Scatter(x=df15.index, y=df15.SMA200_15M, mode='lines', name='SMA200_15M', line_color='#0000ff', line_width=3), row=1, col=3)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBL15_14_2, mode='lines', name='BBL_14_2_15M', line=dict(color='#56a6ae', dash='dash')), row=1, col=3)
    fig.add_trace(go.Scatter(x=df15.index, y=df15.BBU15_14_2, mode='lines', name='BBU_14_2_15M', line=dict(color='#56a6ae', dash='dash')), row=1,  col=3)
    fig.update_xaxes(title_text="Slider - 15 Minute Time Interval", row=1, col=3)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=df15.index, y=df15.volume, marker=dict(color='#7cadf8')), row=2, col=3)

    # Add Day Candlestick Chart
    fig.add_trace(go.Candlestick(x=dfD.index, open=dfD.open, high=dfD.high, low=dfD.low, close=dfD.close),row=1, col=2)
    #fig.add_trace(go.Scatter(x=dfD.index, y=dfD.SMA3_1D, mode='lines', name='SMA3_1D', line_color='#ff00ff'), row=1, col=2)
    fig.update_xaxes(title_text="Slider - 1 Day Time Interval", row=1, col=2)
    fig.update_xaxes(rangeslider_thickness=0.02)
    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=dfD.index, y=dfD.volume, marker=dict(color='#7cadf8')), row=2, col=2)

    # 1 Min Update the time selected zoom
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=1)                      #inset right side by 5 ticks
    formatted_new_time = new_time.strftime("%H:%M")
    end_time_1 = datetime.strptime(formatted_new_time, '%H:%M')
    new_time = current_time - timedelta(minutes=30)                     # set range for plot
    formatted_new_time = new_time.strftime("%H:%M")
    start_time_1 = datetime.strptime(formatted_new_time, '%H:%M')
    last_day = df.index[-1].date()
    start_datetime_1 = datetime.combine(last_day, start_time_1.time())
    end_datetime_1 = datetime.combine(last_day, end_time_1.time())

    # 5 Min Update the time selected zoom to last day view
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=5)                     # inset right side by 5 ticks
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
    new_time = current_time + timedelta(minutes=15)                     # inset right side by 5 ticks
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
    fig.update_xaxes(range=[start_datetime_1, end_datetime_1], row=1, col=5)    # 1 min chart
    fig.update_xaxes(range=[start_datetime_5, end_datetime_5], row=1, col=4)    # 5 min chart
    fig.update_xaxes(range=[start_datetime_15, end_datetime_15], row=1, col=3)  # 15 min chart
    fig.update_xaxes(range=[start_datetime_15, end_datetime_15], row=2, col=3)  # 15 min chart volume
    fig.update_xaxes(range=[start_datetime_5, end_datetime_5], row=2, col=4)    # 5 min chart volume
    fig.update_xaxes(range=[start_datetime_1, end_datetime_1], row=2, col=5)    # 1 min chart volume
    # fig.update_xaxes(range=[start_datetime, end_datetime], row=1, col=2)      # day - full scale default

    Dyn_Ymin = df15.tail(1).low - 1
    Dyn_Ymax = df15.tail(1).high + 1
    #print(Dyn_Ymin.values[0])
    Dyn_Ymin_1min = math.ceil(Dyn_Ymin.values[0] * 0.98)
    Dyn_Ymax_1min = math.floor(Dyn_Ymax.values[0] * 1.02)
    Dyn_Ymin_5min = math.ceil(Dyn_Ymin.values[0] * 0.98)
    Dyn_Ymax_5min = math.floor(Dyn_Ymax.values[0] * 1.02)
    Dyn_Ymin_15min = math.ceil(Dyn_Ymin.values[0] * 0.95)
    Dyn_Ymax_15min = math.floor(Dyn_Ymax.values[0] * 1.05)

    fig.update_yaxes(range=[Dyn_Ymin_15min, Dyn_Ymax_15min], row=1, col=3)
    fig.update_yaxes(range=[Dyn_Ymin_5min, Dyn_Ymax_5min], row=1, col=4)
    fig.update_yaxes(range=[Dyn_Ymin_1min, Dyn_Ymax_1min], row=1, col=5)

    fig.update_yaxes(color='#000000', range=[0, 6000000], row=2, col=3)
    fig.update_yaxes(color='#000000', range=[0, 2000000], row=2, col=4)
    fig.update_yaxes(color='#000000', range=[0, 250000], row=2, col=5)

    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')


    # Update traces name in legend (if on)
    #fig.update_traces(name=Ticker, selector=dict(type='candlestick'))

    #fig.update_layout(title_text=Ticker, xaxis1_rangeslider_visible=True, xaxis2_rangeslider_visible=True,xaxis_rangeslider_thickness=0.02,
    #                  height=1280, width=2500, showlegend=False)
    #fig.update_layout(yaxis=dict(tickmode= 'linear', tick0= Dyn_Ymin, dtick = 0.5 ))
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


    # Show the figure
    fig.show()

