import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from process_data import df, qa_compound_dict


instruments = dict([('Xevo 1', 1), ('Xevo 2', 2)])
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()


standard_a = [
    html.Br(),
    html.Div([
        html.Div(
            className="one-third column left__section",
            children=[
                html.Div(
                    className='chart-titletwo',
                    children=[
                        html.Div([
                            'Instrument:',
                            dcc.RadioItems(
                                id='instruments',
                                options=[{'label': k, 'value': v} for k, v in instruments.items()],
                                value=2,
                                labelStyle={'display': 'inline-block'},
                                style={'margin': '10px 10px 0px'},
                            )]),
                        html.Br(),
                        html.Div([
                            'Date:',
                            dcc.DatePickerSingle(
                                id='dates-picker',
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                date=max_date,
                                style={'margin': '7px 0px'}
                            )],
                            style={
                                'display': 'block',
                                'margin': '8px 0px',
                                'width': "20%"
                            }),
                        html.Br(),
                        html.Div([
                            'Compound:',
                            dcc.Dropdown(
                                id='compound-view',
                                options=[{'label': k, 'value': k} for k, v in qa_compound_dict.items()],
                                value=list(qa_compound_dict.keys())[0],
                                clearable=False,
                                style={
                                    'width': '100%',
                                    'color': 'black',
                                    'margin': '10px 0px 13px'})]),
                        html.Div([
                            'Historical View (Month/Previous N Batches):',
                            daq.BooleanSwitch(
                                id='boolean-switch',
                                on=False,
                                color="#9B51E0",
                                style={'margin': '10px 0px'}
                            ),
                            html.Div(id='boolean-switch-output')
                        ],
                            style={'margin': "40px 0px"})
                    ])],
            style={
                'padding': '30px 70px 70px',
                'background-color': '#a5a5a5',
                'min-height': "100%"}
        ),

        html.Div(
            className='two-thirds column right__section',
            children=[
                html.Div([
                    dcc.Graph(
                        id='stdA-graphic',
                        style={'margin': '0px 9px 30px'},
                    )])],
            style={
                'padding': '30px 5%',
                'min-height': '100%',
                'margin': '0 auto'}
        )],
        style={
            'display': 'flex',
            'background-color': '#f1f1f1'}
    )
]
