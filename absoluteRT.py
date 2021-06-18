import dash_core_components as dcc
import dash_html_components as html
from process_data import df


instruments = dict([('Xevo 1', 1), ('Xevo 2', 2)])
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()


absoluteRT = [
    html.Div(
        children=[
            html.Br(),
            html.H1("Internal Standards aRT Monitor of Calibrator Set"),
            html.P(''' The following table monitors the average absolute retention time (ART) \
                            of each internal standard across the calibrator set for one run against the running \
                            monthly average +/- 2 standard deviations. The running average is calculated from all of \
                            the calibrator sets ran in the listed date range for the selected instrument. The value \
                            in 'Number of Runs' displays the number of runs ran on the selected instrumented during \
                            that month period.'''),
            dcc.DatePickerSingle(
                id='art-date-picker',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                date=max_date),
            dcc.RadioItems(
                id='art-instruments',
                options=[{'label': k, 'value': v} for k, v in instruments.items()],
                value=1,
                labelStyle={'display': 'inline-block'}),
            html.Br(),
            html.Div(id='Runs'),
            html.Br(),
            html.Div(id='art-table-div')
        ],
        className="chart-title")
]
