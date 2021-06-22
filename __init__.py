import base64
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import build_graph
from dash.dependencies import Input, Output
from dash_table.Format import Format, Scheme
from histogram import histogram
from averages import averages
from batch import batch
from standard_a import standard_a
from absoluteRT import absoluteRT
from process_data import df, qa_compound_dict, compound_dict, int_std_dict
import pathlib


actual_dir = pathlib.Path().absolute()

app = dash.Dash(__name__)
server = app.server

image_filename = f'{actual_dir}/dashboard_files/uwmedlogo.png'
uwlabmed_filename = f'{actual_dir}/dashboard_files/uwlabmed.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
labmed_encoded_image = base64.b64encode(open(uwlabmed_filename, 'rb').read())
instruments = dict([('Xevo 1', 1), ('Xevo 2', 2)])
time_frames = ['Daily', 'Weekly', 'Monthly']
parameters = {'Internal Standard Signal': "is_peak_area",
              'Ion Ratio': "ion_ratio",
              'Relative Retention Time': "rrt",
              'Signal-to-Noise': "SN"}

app.layout = html.Div([
    html.Header(
        children=[
            'Opiate LCMS Dashboard',
            html.Img(
                src='data:image/png;base64,{}'.format(encoded_image.decode()),
                style={
                    'height': '17px',
                    'width': '128px',
                    'float': 'left',
                    'margin-top': '15px',
                    'margin-left': '15px'})
            ],
        style={'textAlign': 'center',
               'color': '#ffffff',
               'background-color': '#363C74',  # '#4b2e83',
               'width': '100%',
               'margin': '0 auto 0 auto',
               'font': '20px Georgia, serif',
               'line-height': '50px',
               'height': '50px',
               'max-height': '75px',
               'vertical-align': 'top'}
    ),
    dcc.Tabs(id="tabs", value='Tab-Hist', parent_className='custom-tabs', children=[
        dcc.Tab(
            label='Histograms',
            className='custom-tab',
            value='Tab-Hist',
            selected_className='custom-tab--selected',
            children=histogram
            ),
        dcc.Tab(
            label='Averages',
            className='custom-tab',
            selected_className='custom-tab--selected',
            value='Tab-Avg',
            children=averages
        ),
        dcc.Tab(
            label='Batch',
            className='custom-tab',
            selected_className='custom-tab--selected',
            value='Tab-Batch',
            children=batch
        ),
        dcc.Tab(
            label='Standard-A',
            value='Tab-StdA',
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=standard_a
        ),
        dcc.Tab(
            label='absolute RT',
            value='Tab-art',
            selected_className='custom-tab--selected',
            className='custom-tab',
            children=absoluteRT)
        ]),
    html.Div([
        html.Img(
            src='data:image/png;base64,{}'.format(labmed_encoded_image.decode()),
            style={
                'height': '89px',
                'width': '225px',
                'margin': '30px auto',
                'margin-top': "70px",
                'display': 'block'
                })])
])


@app.callback(
    Output('histogram-graphic', 'figure'),
    [Input('sample-types', 'value'),
     Input('instrument', 'value'),
     Input('hist-compound', 'value'),
     Input('hist-parameters', 'value'),
     Input('date-range-hist', 'start_date'),
     Input('date-range-hist', 'end_date')])
def update_hist_graph(sample_types, xevo, hist_compnd, hist_param, start_date, end_date):
    # Instrument Type
    dff = df[df['Xevo'] == xevo]

    # Sample Type
    if sample_types != 'All':
        dff = dff[dff['sample_type'].str.contains(sample_types)]
    sample_types = sample_types.replace("|", " & ")

    # Date Range
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    mask = (dff['Date'] >= start_date) & (dff['Date'] <= end_date)
    dff = dff.loc[mask]

    oob_string = 'Below QA Cutoff'
    xaxislabel = [param for param, value in parameters.items() if value == hist_param][0]

    if hist_param == 'is_peak_area':
        int_std = compound_dict[hist_compnd]
        dff = dff[dff['int_std'] == int_std]
        graph_title = int_std
        x_val = int_std_dict[int_std]
        shape, annotation = build_graph.create_vertical_line(x_val)
        _, percent_oob = build_graph.calculate_below_bound(dff, x_val, hist_param)
    else:
        dff = dff[dff['compound'] == hist_compnd]
        graph_title = hist_compnd
        param_qa_dict = {'ion_ratio': {'value': 'ion_ratio_avg', 'round_value': 3},
                         'rrt': {'value': 'rel_reten', 'round_value': 3},
                         'SN': {'value': 'signoise_stda', 'round_value': 1}}

        qa_compound = qa_compound_dict[hist_compnd]
        values = param_qa_dict[hist_param]
        round_value = values['round_value']
        x_val = round(qa_compound[values['value']], round_value)
        shape, annotation = build_graph.create_vertical_line(x_val)
        if hist_param == 'SN':
            _, percent_oob = build_graph.calculate_below_bound(dff, x_val, hist_param)
        else:
            if hist_param == 'rrt':
                high = qa_compound['rel_reten_high']
                low = qa_compound['rel_reten_low']
            else:
                low = qa_compound['ion_ratio_low']
                high = qa_compound['ion_ratio_high']
            vertical_boundaries = build_graph.create_vertical_range_lines(low, high)
            shape.append(vertical_boundaries)
            _, percent_oob = build_graph.calculate_out_of_range(dff, low, high, hist_param)
            oob_string = 'Out of QA Range'

    return {
        'data': [dict(
            type='histogram',
            x=dff[hist_param],
            text=hist_param
        )],
        'layout': dict(
            title=f'{graph_title} with {sample_types} sample types <br> {percent_oob}% {oob_string}',
            xaxis={'title': xaxislabel},
            yaxis={'title': 'Number of samples'},
            margin={'l': 70, 'b': 40, 't': 80, 'r': 0},
            hovermode='closest',
            shapes=shape,
            annotations=annotation
        )
    }


@app.callback(
    [Output('averages-graphic', 'figure'),
     Output('avg-table-div', 'children')],
    [Input('avg-time-frame', 'value'),
     Input('avg-parameters', 'value'),
     Input('avg-sample-type', 'value'),
     Input('cmpd-options', 'value'),
     Input('avg-instrument', 'value')])
def update_avg_graph(time_frame, avg_param, avg_sample_type, avg_compound, xevo):
    # Sample Type
    if avg_sample_type != 'All':
        dfa = df[df['sample_type'].str.contains(avg_sample_type)]
    else:
        dfa = df
    # Obtain statistical data for display
    df_mean, df_std = build_graph.calculate_avg_data(dfa, avg_param, time_frame, xevo)

    # Assess parameter and build lines and annotations accordingly
    if avg_param == 'is_peak_area':
        y_title = 'IS Peak Area'
        avg_compound = compound_dict[avg_compound]
        qa_val = int_std_dict[avg_compound]
        shape, annotation = build_graph.create_horizontal_line(qa_val)
        num_type = int
        number_format = "{:,}"
    else:
        param_qa_dict = {'ion_ratio': 'ion_ratio_avg',
                         'rrt': 'rel_reten',
                         'SN': 'signoise_stda'}
        num_type = float
        number_format = "{:.1f}"
        qa_compound = qa_compound_dict[avg_compound]
        qa_val = qa_compound[param_qa_dict[avg_param]]
        shape, annotation = build_graph.create_horizontal_line(qa_val)
        y_title = 'SigNoise'
        if avg_param == 'rrt':
            y_title = 'Relative RT'
            high = qa_compound['rel_reten_high']
            low = qa_compound['rel_reten_low']
            horizontal_range = build_graph.create_horizontal_range_lines(low, high, avg_param)
            shape.append(horizontal_range)
            number_format = "{:.3f}"
        elif avg_param == 'ion_ratio':
            y_title = 'Ion Ratio'
            low = qa_compound['ion_ratio_low']
            high = qa_compound['ion_ratio_high']
            horizontal_range = build_graph.create_horizontal_range_lines(low, high, avg_param)
            shape.append(horizontal_range)
            number_format = "{:.3f}"

    std_list = df_std[avg_compound].tolist()
    mean_df = pd.DataFrame(df_mean[avg_compound]).reset_index()
    mean_df.columns = ['Date', 'Average']
    std_df = pd.DataFrame(df_std[avg_compound]).reset_index()
    std_df.columns = ['Date', 'Std Dev']
    table_df = pd.merge(mean_df, std_df, on='Date')
    table_df['Lower Bound'] = table_df['Average'] - table_df['Std Dev']
    table_df['Upper Bound'] = table_df['Average'] + table_df['Std Dev']
    table_cols = list(table_df)
    table_df[table_cols[1:]] = table_df[table_cols[1:]].astype(num_type)
    for col in table_cols[1:]:
        table_df[col] = table_df[col].apply(number_format.format)
    table_columns = [{'name': i, 'id': i} for i in table_cols]
    table_df['Date'] = pd.to_datetime(table_df.Date)
    table_df['Date'] = table_df['Date'].dt.strftime('%m/%d/%Y')

    if time_frame == 'Weekly':
        fig_title = 'Weekly Average by Date (Start:Tue, End:Mon)'
        text = 'Week of '
        tformat = "%m/%d/%y"
    elif time_frame == 'Daily':
        fig_title = f'{time_frame} Average'
        text = ''
        tformat = "%m/%d/%y"
    else:
        fig_title = f'{time_frame} Average'
        text = "Month of "
        tformat = "%b"

    return {
        'data': [dict(
            x=df_mean.index,
            y=df_mean[avg_compound],
            mode='markers',
            text=text + df_mean.index.strftime(tformat),
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
                },
            error_y=dict(
                type='data',  # value of error bar given in data coordinates
                array=std_list)
            )],
        'layout': dict(
            title=avg_compound,
            xaxis={'title': fig_title},
            yaxis={'title': f'{y_title} (+/- 1 Std Dev)'},
            margin={'l': 70, 'b': 40, 't': 80, 'r': 0},
            hovermode='closest',
            shapes=shape,
            annotations=annotation
            )
        }, html.Div([dash_table.DataTable(
            id='avg-table',
            columns=table_columns,
            data=table_df.to_dict("records"),
            style_cell={'textAlign': 'center'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            fixed_rows={'headers': True},
            style_table={'height': 400}
            )])


@app.callback(
    [Output('batch-graphic', 'figure'),
     Output('table-div', 'children')],
    [Input('lcms-parameters', 'value'),
     Input('view-compound', 'value'),
     Input('batch-instrument', 'value'),
     Input('batch-sample-type', 'value'),
     Input('date-pick-batch', 'date')])
def update_inj_graph(parameter, opiate, instrument, batch_sample_type, date):
    param_qa_dict = {'ion_ratio': 'ion_ratio_avg',
                     'rrt': 'rel_reten',
                     'SN': 'signoise_stda'}
    # Instrument Selection
    dff = df[df['Xevo'] == instrument]

    # Date
    dff = dff[dff['Date'] == pd.to_datetime(date)]

    # Sample Type
    if batch_sample_type != 'All':
        dff = dff[dff['sample_type'].str.contains(batch_sample_type)]

    # Create lines, annotations, and generate statistics for summary table
    if parameter == 'is_peak_area':
        int_std = compound_dict[opiate]
        qa_val = int_std_dict[int_std]
        dff = dff[dff['int_std'] == int_std]
        is_mean = dff['is_peak_area'].mean()
        is_std = dff['is_peak_area'].std()
        graph_title = int_std
        low_std = is_mean - (is_std * 2)
        high_std = is_mean + (is_std * 2)

        shape, annotation = build_graph.create_horizontal_line(qa_val)
        horizontal_range = build_graph.create_horizontal_range_lines(low_std, high_std, parameter)
        avg_shape = build_graph.create_avg_line_shape(is_mean, parameter)
        shape += avg_shape
        shape.append(horizontal_range)
        total_oob, percent_oob = build_graph.calculate_out_of_range(dff, low_std, high_std, parameter)

        stat_list = [int_std,
                     int(round(is_mean)),
                     int(round(is_std)),
                     int(round(low_std)),
                     int(round(high_std))] + [total_oob, percent_oob]
        columns = ['Int Std', 'Average', 'Stnd Dev', '-2 Std Dev', '+2 Std Dev', 'No. Out of Bounds', '% Out of Bounds']
        data_table_columns = [{'name': i, 'id': i} for i in columns]
        df_stat = pd.DataFrame([stat_list], columns=columns)
    elif parameter == 'SN':
        graph_title = opiate
        dff = dff[dff['compound'] == opiate]
        qa_compound = qa_compound_dict[opiate]
        qa_val = qa_compound[param_qa_dict[parameter]]
        shape, annotation = build_graph.create_horizontal_line(qa_val)

        number_oob, percent_oob = build_graph.calculate_below_bound(dff, qa_val, parameter)
        stat_list = [opiate, round(qa_val, 1)] + [number_oob, percent_oob]
        columns = ['Compound', 'QA Value', '# Below Cutoff', "% Below Cutoff"]
        data_table_columns = [{'name': i, 'id': i} for i in columns]
        df_stat = pd.DataFrame([stat_list], columns=columns)
    else:
        graph_title = opiate
        dff = dff[dff['compound'] == opiate]
        qa_compound = qa_compound_dict[opiate]
        qa_val = qa_compound[param_qa_dict[parameter]]
        if parameter == 'rrt':
            high = qa_compound['rel_reten_high']
            low = qa_compound['rel_reten_low']
            delta = round(((high - qa_val)/qa_val)*100, 1)

        else:
            low = qa_compound['ion_ratio_low']
            high = qa_compound['ion_ratio_high']
            delta = int(float(qa_compound['ion_ratio_cv']) * 100)

        shape, annotation = build_graph.create_horizontal_line(qa_val)
        horizontal_range = build_graph.create_horizontal_range_lines(low, high, parameter)
        shape.append(horizontal_range)
        total_oob, percent_oob = build_graph.calculate_out_of_range(dff, low, high, parameter)

        stat_list = [opiate,
                     round(qa_val, 3),
                     str(int(round(delta))) + '%',
                     round(low, 3),
                     round(high, 3)] + [total_oob, percent_oob]
        columns = ['Compound', 'QA', 'CV', 'Lower Bound', 'Upper Bound', 'No. Out of Bounds', '% Out of Bounds']
        data_table_columns = [{'name': i, 'id': i} for i in columns]
        df_stat = pd.DataFrame([stat_list], columns=columns)

    title_dic = dict()
    for k, v in parameters.items():
        title_dic[v] = k

    return {
        'data': [dict(
            x=dff['sample_id'],
            y=dff[parameter],
            text=dff['sample'],
            mode='markers',
            name='Sample(s)',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
                })
            ],
        'layout': dict(
            title=graph_title,
            xaxis={'title': 'Injection Sequence/Sample ID'},
            yaxis={'title': title_dic[parameter]},
            margin={'l': 70, 'b': 40, 't': 80, 'r': 10},
            hovermode='closest',
            shapes=shape,
            annotations=annotation)
        }, html.Div([
            dash_table.DataTable(
                id='table',
                columns=data_table_columns,
                data=df_stat.to_dict("records"),
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'},
                style_cell={'textAlign': 'left'}
            )])


@app.callback(
    [Output('stdA-graphic', 'figure'),
     Output('boolean-switch-output', 'children')],
    [Input('dates-picker', 'date'),
     Input('instruments', 'value'),
     Input('boolean-switch', 'on'),
     Input('compound-view', 'value')])
def stda_graph(date_a, xevo, histbool, stda_cmpnd):
    # Instrument
    dff = df[df['Xevo'] == xevo]
    # Limit data to Standard-A
    dff = dff[dff['sample'] == 'StdA']
    # Set Dates
    end_date = pd.to_datetime(date_a)
    if histbool:
        colour = "#9B51E0"
        mod_time_df = dff['Date'] <= end_date
        dff = dff.loc[mod_time_df]
        dates = dff['Date'].unique()
        dates.sort()
        if len(dates) >= 10:
            start_date = dates[-10]
            time_view = 'Previous 10 Batches'
        else:
            start_date = dates[0]
            time_view = f'Previous {len(dates)} Batches'
    else:
        time_view = '1 Month View'
        colour = '#85754d'
        start_date = end_date + pd.DateOffset(months=-1)
        start_date = pd.to_datetime(start_date.date())

    mask = (dff['Date'] >= start_date) & (dff['Date'] <= end_date)
    dff = dff.loc[mask]
    dff = dff[dff['compound'] == stda_cmpnd]

    return {
        'data': [dict(
            x=dff['Date'],
            y=round(dff['peak_area'], 0),
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {
                    'width': 0.5,
                    'color': 'white'}
                })
            ],
        'layout': dict(
            title=f'Peak Area of Std-A for<br />{stda_cmpnd}',
            xaxis={'title': 'Dates'},
            yaxis={'title': 'Peak Area'},
            margin={'l': 70, 'b': 40, 't': 100, 'r': 0},
            plot_bgcolor='#f1f1f1',
            paper_bgcolor='#f1f1f1',
            hovermode='closest')
        }, html.Div([time_view],
                    style={
                        'font-style': 'italic',
                        'font-size': "16px",
                        'text-align': 'center',
                        'color': colour})


@app.callback(
    [Output('Runs', 'children'),
     Output('art-table-div', 'children')],
    [Input('art-date-picker', 'date'),
     Input('art-instruments', 'value')])
def art_output(date, xevo):
    # Instrument
    dff = df[df['Xevo'] == xevo]
    # Limit the samples to calibrators (or Standards)
    dff = dff[dff['sample_type'] == 'calibrator']

    # Collect either last ten runs or X < 10 runs
    end_date = pd.to_datetime(date)
    dates = sorted(dff['Date'].unique())
    if len(dates) >= 10:
        start_date = pd.to_datetime(dates[-10])
        numb = '10'
    else:
        start_date = pd.to_datetime(dates[0])
        numb = str(len(dates))
    mask = (dff['Date'] >= start_date) & (dff['Date'] <= end_date)
    dff = dff.loc[mask]

    # Calculate Running Average
    df_pivot_month = pd.pivot_table(dff, values='is_RT', index="results_pkey", columns='int_std')
    month_mean = df_pivot_month.mean(axis=0)
    month_std = df_pivot_month.std(axis=0)

    # Calculate Day Average
    temp_df = dff[dff['Date'] == end_date]
    df_pivot_day = pd.pivot_table(temp_df, values='is_RT', index="sample", columns='int_std', dropna=False)
    if len(df_pivot_day) > 5:
        raise ValueError(f'More than 5 calibrator injectionsa were found for the run on {end_date}')
    day_mean = df_pivot_day.mean(axis=0)

    display_df = pd.concat([day_mean, month_mean, month_std], axis=1).reset_index()
    display_df.columns = ['Internal Standard', 'Day Average', 'Running Avg', 'SD']
    display_df['-2 SD'] = display_df['Running Avg'] - (2 * display_df['SD'])
    display_df['+2 SD'] = display_df['Running Avg'] + (2 * display_df['SD'])
    del display_df['SD']
    display_columns = list(display_df)
    display_columns = [{'name': i, 'id': i, 'type': 'text'} for i in display_columns]
    for column in display_columns[1:]:
        column['type'] = 'numeric'
        column['format'] = Format(scheme=Scheme.fixed, precision=3)
    end_string = end_date.strftime("%b %d, %Y")
    start_string = start_date.strftime("%b %d, %Y")

    return html.Div([
        html.P(f'Date Range: {start_string} to {end_string}'),
        html.P(f'Number of Runs: {numb}')]), \
        html.Div([
            dash_table.DataTable(
                id='aRT-table',
                columns=display_columns,
                data=display_df.to_dict("records"),
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'},
                style_cell={'textAlign': 'left'},
                style_data_conditional=[{
                    'if': {'column_id': 'Day Average'},
                    'backgroundColor': '#008000',
                    'color': 'white'},
                    {'if': {'filter_query': '{Day Average} > {+2 SD} || {Day Average} < {-2 SD}',
                            'column_id': 'Day Average'},
                        'backgroundColor': '#FF0000',
                        'color': 'white'}
                ])
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
