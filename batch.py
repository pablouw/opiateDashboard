import dash_core_components as dcc
import dash_html_components as html
from process_data import available_samples, df, qa_compound_dict


instruments = dict([('Xevo 1', 1), ('Xevo 2', 2)])
parameters = {'Internal Standard Signal': "is_peak_area",
              'Ion Ratio': "ion_ratio",
              'Relative Retention Time': "rrt",
              'Signal-to-Noise': "SN"}
available_options = [{'label': i.replace('|', ' / '), 'value': i} for i in available_samples]
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()


batch = [
    html.Br(),
    html.Div([
        html.Div(
            className='chart-title',
            children=[
                html.Div(
                    children=[
                        'MS Instrument:',
                        dcc.RadioItems(
                            id='batch-instrument',
                            options=[{'label': k, 'value': v} for k, v in instruments.items()],
                            value=2,
                            labelStyle={
                                'display': 'inline-block',
                                'padding': '5px'})
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 2px 4px 0px",
                        'vertical-align': 'top',
                        'width': "17%"}),
                html.Div(
                    children=[
                        'LCMS Parameter:',
                        dcc.Dropdown(
                            id='lcms-parameters',
                            options=[{'label': k, 'value': v} for k, v in parameters.items()],
                            value=list(parameters.values())[0],
                            clearable=False)
                    ],
                    style={
                        'width': '22%',
                        'padding': '2px 2px 4px',
                        'display': 'inline-block'}),
                html.Div(
                    children=[
                        'Compound:',
                        dcc.Dropdown(
                            id='view-compound',
                            options=[{'label': k, 'value': k} for k, v in qa_compound_dict.items()],
                            value=list(qa_compound_dict.keys())[0],
                            clearable=False)
                    ],
                    style={
                        'width': '22%',
                        'padding': '2px 2px 4px',
                        'display': 'inline-block'}),
                html.Div(
                    children=[
                        'Sample Type:',
                        dcc.Dropdown(
                            id='batch-sample-type',
                            options=available_options,
                            value='All',
                            clearable=False)
                    ],
                    style={
                        'width': '22%',
                        'padding': '2px 0px 4px 2px',
                        'display': 'inline-block'}),
                html.Div(
                    children=[
                        'Batch Date:',
                        dcc.DatePickerSingle(
                            id='date-pick-batch',
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=min_date,
                            style={
                                'display': 'block',
                            })
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': "2px 0px 4px 12px",
                        'vertical-align': 'top',
                        'width': '13%'}
                )]),
    ],
        style={
            'borderTop': '2px solid #d1d1d1',
            'borderBottom': '8px solid #d1d1d1'}
    ),
    dcc.Graph(
        id='batch-graphic'
    ),
    html.Br(),
    html.Div(
        id='table-div',
        className='chart-title',
        style={
            'borderTop': '4px solid #d1d1d1',
            'borderBottom': '8px solid #d1d1d1'}
    )
]
