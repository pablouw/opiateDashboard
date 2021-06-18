import numpy as np
import pandas as pd


def calculate_timeframe_avg(data, timeframe):
    if timeframe == 'Weekly':
        mean = data.resample('W-MON', on='Date').mean().reset_index().sort_values(by='Date')
        std = data.resample('W-MON', on='Date').std().reset_index().sort_values(by="Date")
        mean['Date'] = mean['Date'] - pd.Timedelta(days=6)
        std['Date'] = std['Date'] - pd.Timedelta(days=6)
        return mean, std
    elif timeframe == 'Daily':
        mean = data.resample('D', on='Date').mean().reset_index().sort_values(by='Date')
        std = data.resample('D', on='Date').std().reset_index().sort_values(by='Date')
        return mean, std
    elif timeframe == 'Monthly':
        mean = data.resample('M', on='Date').mean().reset_index().sort_values(by='Date')
        std = data.resample('M', on='Date').std().reset_index().sort_values(by='Date')
        return mean, std
    else:
        raise ValueError('A valid time frame must be selected.')


def calculate_avg_data(data, lc_param, time_frame='Weekly', instrument=2):
    data = data[data['Xevo'] == instrument]
    if lc_param == 'is_peak_area':
        columns = 'int_std'
    else:
        columns = 'compound'
    data = pd.pivot_table(data, values=lc_param, index=['results_pkey', "Date"], columns=columns)
    data = data.reset_index().drop(columns='results_pkey')
    data.rename_axis(None, axis=1, inplace=True)
    data_mean, data_std = calculate_timeframe_avg(data, time_frame)
    data_mean = data_mean.set_index('Date')
    data_mean = data_mean.dropna(how='all')
    data_std = data_std.set_index('Date')
    data_std = data_std.dropna(how='all')
    return data_mean, data_std


def create_horizontal_line(y_value):
    line_shape = [dict(
        xref='paper',
        x0=0,
        x1=1,
        y0=y_value,
        y1=y_value,
        type='line',
        name=str(y_value),
        opacity=0.5,
        line={'dash': 'dash'}
    )]
    line_annotation = [dict(
        showarrow=False,
        text=f'QA: {str(round(y_value, 3))}',
        align='right',
        y=y_value,
        xanchor='right',
        xref='paper',
        x=1,
        yanchor='bottom'
    )]
    return line_shape, line_annotation


def create_avg_line_shape(y_avg, parameter):
    param_colors = {'is_peak_area': {'color': 'Purple', 'dash': 'dot'}}
    line = param_colors[parameter]
    avg_line, _ = create_horizontal_line(y_avg)
    avg_line[0]['line'] = line
    return avg_line


def create_horizontal_range_lines(low, high, param):
    param_colors = {'rrt': {'fillcolor': 'LightSalmon'},
                    'ion_ratio': {'fillcolor': 'lightgoldenrodyellow'},
                    'is_peak_area': {'fillcolor': "PaleTurquoise"}
                    }
    fillcolor = param_colors[param]['fillcolor']
    horizontal_shape = dict(
        type="rect",
        xref="paper",
        x0=0,
        y0=low,
        x1=1,
        y1=high,
        fillcolor=fillcolor,
        opacity=0.5,
        layer="below",
        line_width=0)
    return horizontal_shape


def create_vertical_line(x_val):
    vert_line = [dict(
        yref='paper',
        x0=x_val,
        x1=x_val,
        y0=0,
        y1=1,
        type='line',
        name=str(x_val),
        opacity=0.5,
        line={'dash': 'dash'}
    )]
    vert_annotation = [dict(
        showarrow=False,
        text=str(x_val),
        textangle=90,
        align='left',
        x=x_val,
        xanchor="right",
        yref='paper',
        y=1,
        yanchor="top")]

    return vert_line, vert_annotation


def create_vertical_range_lines(low, high):
    vertical_shape = dict(
        type="rect",
        yref="paper",
        y0=0,
        y1=1,
        x0=low,
        x1=high,
        fillcolor='red',
        opacity=0.3,
        layer="below",
        line_width=0)

    return vertical_shape


def calculate_out_of_range(limited_df, low_limit, upp_limit, parameter):
    limited_df = limited_df.replace([np.inf, -np.inf], np.nan)
    limited_df = limited_df[limited_df[parameter].notna()]
    positive_list = list(limited_df[parameter])
    lower = len([i for i in positive_list if i < low_limit])
    upper = len([j for j in positive_list if j > upp_limit])
    total = lower + upper
    percent = round(total / len(limited_df[parameter]) * 100, 1)
    return total, percent


def calculate_below_bound(limited_df, lloq, parameter):
    limited_df = limited_df.replace([np.inf, -np.inf], np.nan)
    limited_df = limited_df[limited_df[parameter].notna()]
    positives_list = list(limited_df[parameter])
    num_oob = len([i for i in positives_list if i < lloq])
    perc_oob = round(num_oob / len(positives_list) * 100, 1)
    return num_oob, perc_oob
