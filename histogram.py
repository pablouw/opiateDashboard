import dash_core_components as dcc
import dash_html_components as html
from process_data import available_samples, df, qa_compound_dict


instruments = dict([('Xevo 1', 1), ('Xevo 2', 2)])
time_frames = ['Daily', 'Weekly', 'Monthly']
parameters = {'Internal Standard Signal': "is_peak_area",
              'Ion Ratio': "ion_ratio",
              'Relative Retention Time': "rrt",
              'Signal-to-Noise': "SN"}
available_options = [{'label': i.replace('|', ' / '), 'value': i} for i in available_samples]
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()


histogram = [
    html.Br(),
    html.Div([
        html.Div(
            className='chart-title',
            children=[
                html.Div(
                    children=[
                        'MS Instrument:',
                        dcc.RadioItems(
                            id='instrument',
                            options=[{'label': k, 'value': v} for k, v in instruments.items()],
                            value=2,
                            labelStyle={'display': 'inline-block'},
                            style={'padding': '5px'}
                        )],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 2px 4px 0px",
                        'vertical-align': 'top',
                        'width': "17%"}),
                html.Div(
                    children=[
                        'Sample Type:',
                        dcc.Dropdown(
                            id='sample-types',
                            options=available_options,
                            value='All',
                            clearable=False)
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 2px 4px 2px",
                        'width': "18%"}),
                html.Div(
                    children=[
                        'LCMS Parameter:',
                        dcc.Dropdown(
                            id='hist-parameters',
                            options=[{'label': k, 'value': v} for k, v in parameters.items()],
                            value=list(parameters.values())[0],
                            clearable=False)
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 2px 4px 2px",
                        'width': "19%"}),
                html.Div(
                    children=[
                        'Compound:',
                        dcc.Dropdown(
                            id='hist-compound',
                            options=[{'label': k, 'value': k} for k, v in qa_compound_dict.items()],
                            value=list(qa_compound_dict.keys())[0],
                            clearable=False)
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 2px 4px 2px",
                        'width': "19%"}),
                html.Div(
                    children=[
                        'Date Range:',
                        dcc.DatePickerRange(
                            id='date-range-hist',
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            initial_visible_month=min_date,
                            start_date=min_date,
                            end_date=max_date,
                            style={
                                'display': 'block',
                                # 'line-height': '22px',
                                # 'padding': '5px 5px 4px',
                                'font-size': '8px',
                            })
                    ],
                    style={
                        'display': 'inline-block',
                        'vertical-align': 'top',
                        'padding': "2px 0px 4px 12px",
                        'width': '25%'}
                )]
        )],
        style={
            'borderTop': '2px solid #d1d1d1',
            'borderBottom': '8px solid #d1d1d1'}),
    html.Br(),
    html.Br(),
    dcc.Graph(id='histogram-graphic')
]
