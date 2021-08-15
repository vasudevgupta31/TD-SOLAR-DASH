"""
main dash run app
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from numpy import inf, nan
import funcs
import config

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

app_colors = {'background': config.GRAPH_BG,
              'text': '#cccccc',
              'grid': config.GRID_COL,
              'axis': "#323130"}

# DEF OPTIONS
site_options = funcs.get_site_options(destination=config.real_path)
min_date, max_date = funcs.get_min_max_dates(config.real_path,
                                             config.logs_path,
                                             config.day_ahead_ensemble_path,
                                             config.satellite_forecast_path)
output_lines = funcs.get_outputs_to_show()


def serve_layout():
    return html.Div(
        children=[
            html.Div(
                className="row",
                children=[
                    # COL » Options
                    html.Div(
                        className="four columns div-user-controls",
                        children=[
                            html.Img(className="logo", src=app.get_asset_url("logo_final.png"),
                                     style={'width': '300px',
                                            'height': '200px',
                                            "display": "inline-block",
                                            'margin-left': '0.1%'}),
                            html.H2("Solar Forecast"),
                            html.P("""Select different Day & Site using the Date and Site picker."""),
                            html.Div(className="div-for-dropdown",
                                     children=[
                                         dcc.DatePickerSingle(id="date-picker",
                                                              min_date_allowed=min_date,
                                                              max_date_allowed=max_date,
                                                              initial_visible_month=funcs.get_today_date(),
                                                              date=funcs.get_today_date(),
                                                              display_format="MMMM D, YYYY",
                                                              persistence=True,
                                                              persistence_type='local',
                                                              style={"border": "0px solid black"})
                                     ]),
                            html.Div(className="row",
                                     children=[
                                         html.Div(className="div-for-dropdown",
                                                  children=[
                                                      # Dropdown for locations on map
                                                      dcc.Dropdown(id="site-dropdown",
                                                                   options=site_options,
                                                                   # value='NR_Solar',
                                                                   persistence=True,
                                                                   persistence_type='local',
                                                                   placeholder="Select a location")
                                                  ])]),

                            html.Div(
                                className="div-for-dropdown",
                                children=[html.H6("""Select Outputs :"""),
                                          # Dropdown to select times
                                          dcc.Checklist(
                                              id="output-selector",
                                              options=output_lines,
                                              value=['Actual', 'Day Ahead Ensemble', 'IntraDay'],
                                              persistence=True,
                                              persistence_type='local',
                                              # labelStyle={'display': 'inline-block'},
                                              style={'font': 'Open Sans',
                                                     'font-size': '14px',
                                                     'padding-left': '12px',},
                                              inputStyle={"margin-right": "5px"}
                                          )
                                          ],
                            ),
                            html.H6(children=['Displaying in Dashboard:']),
                            html.P(id="showing-date"),
                            html.P(id="showing-site"),
                            # html.P(id="date-value"),
                            html.P(id='updated-at'),
                            dcc.Markdown(
                                children=[
                                    "Learn More at: [TensorDynamics](https://tensordynamics.in/)"
                                ])
                        ]),
                    # COL » Graphs
                    html.Div(
                        className="eight columns div-for-charts bg-grey",
                        children=[
                            dcc.Interval(id='interval-component',
                                         interval=60 * config.REFRESH_RATE * 1000,  # in milliseconds i.e. 1*1000=1 sec
                                         n_intervals=0),
                            html.Div(className="graph-headers", children=["Actual Power vs Forecast"],
                                     style={'textAlign': 'center'}),
                            dcc.Graph(id="solar-graph"),
                            html.Div(className="graph-headers", children=["Error %"], style={'textAlign': 'center'}),
                            dcc.Graph(id="error_graph")
                        ])
                ])
        ])


# Callback 1
@app.callback(Output('solar-graph', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('date-picker', 'date'),
               Input('interval-component', 'n_intervals'),
               Input('output-selector', 'value')])
def update_graph(site, date, n, outputs):
    if site is None:
        site = 'NR_Solar'
    if len(outputs) == 0:
        outputs = ['Actual']

    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
    data = funcs.read_all_data_for_date_site(real_path=config.real_path,
                                             log_path=config.logs_path,
                                             intra_day_path=config.intra_day_path,
                                             satellite_forecast_path=config.satellite_forecast_path,
                                             day_ahead_ensemble_path=config.day_ahead_ensemble_path,
                                             date=date,
                                             site=site)
    # Filter accord to output-selector
    if 'Logs' in outputs:
        for col in data.columns:
            if ':' in col:
                outputs = outputs + [col]
        outputs.remove('Logs')
        log_col1 = [col for col in data.columns if ':' in col][0]
        log_col2 = [col for col in data.columns if ':' in col][1]
    else:
        log_col1, log_col2 = None, None

    data = data[outputs]
    data = data.reindex(sorted(data.columns), axis=1)

    color_codes = {'IntraDay': 'orange',
                   'Day Ahead Ensemble': 'blue',
                   'Actual': 'green',
                   'Satellite': 'yellow',
                   log_col1: 'darkgray',
                   log_col2: 'lightgray'}

    color_dict = {'green': 'rgb(153, 201, 69)',
                  'blue': 'rgb(102, 197, 204)',
                  'orange': 'rgb(248, 156, 116)',
                  'yellow': 'rgb(246, 207, 113)',
                  'darkgray': 'rgb(102, 102, 102)',
                  'lightgray': 'rgb(204, 204, 204)'}

    col_seq = [color_dict.get(color_codes.get(col)) for col in data.columns]

    fig = px.line(data_frame=data,
                  y=data.columns,
                  x=data.index,
                  template='gridon',
                  hover_name=data.index,
                  color_discrete_sequence=col_seq,
                  # color_discrete_sequence=px.colors.qualitative.Safe,
                  # color_discrete_sequence=px.colors.qualitative.Pastel,
                  height=config.G1_HEIGHT)

    # X Axis
    fig.update_xaxes(tickfont=dict(color=app_colors['text'], size=config.AXIS_TICK_SIZE),
                     showgrid=True,
                     #gridcolor=app_colors['grid']
                     )

    # Y Axis
    fig.update_yaxes(tickfont=dict(color=app_colors['text'], size=config.AXIS_TICK_SIZE),
                     linecolor=app_colors['axis'], showgrid=True,
                     #gridcolor=app_colors['grid']
                     )

    fig.update_layout(  # title_text=f"<b> {site}<b>",
        # title_x=0.50,
        xaxis_title=None,
        yaxis_title="Power (MW)",
        showlegend=True,
        legend_title='',
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.95,
                    xanchor="right",
                    x=1),
        font_family='Open Sans',
        font=dict(size=config.GEN_FONT_GRAPHS,
                  color=app_colors['text']),
        hoverlabel=dict(bgcolor=app_colors['background'],
                        font_size=config.HOVER_SIZE),
        plot_bgcolor=app_colors['background'],
        paper_bgcolor=app_colors['background'],
        xaxis_tickformat='%H:%M',
        yaxis_tickformat=',')

    fig.update_layout(hovermode="x unified")
    fig.update_traces(mode="markers+lines", hovertemplate=None)

    return fig


# Callback 2
@app.callback(Output('error_graph', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('date-picker', 'date'),
               Input('interval-component', 'n_intervals')])
def update_graph(site, date, n):
    if site is None:
        site = 'NR_Solar'
    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
    data = funcs.read_all_data_for_date_site(real_path=config.real_path,
                                             log_path=config.logs_path,
                                             intra_day_path=config.intra_day_path,
                                             satellite_forecast_path=config.satellite_forecast_path,
                                             day_ahead_ensemble_path=config.day_ahead_ensemble_path,
                                             date=date,
                                             site=site)
    show_cols = config.error_bars_for
    if len(show_cols) > 1:
        raise ValueError("The error graphs are only supported for maximum one output. "
                          "Please check 'show_cols' in config")
    else:
        show_cols = show_cols[0]

    # CALC ERROR
    data = data[['Actual', show_cols]]

    data[show_cols] = (abs(data[show_cols] - data['Actual']) / data['Actual'])
    data.replace([inf, -inf], nan, inplace=True)
    data.drop('Actual', axis=1, inplace=True)

    color_dict = {'green': 'rgb(153, 201, 69)',
                  'blue': 'rgb(102, 197, 204)',
                  'orange': 'rgb(248, 156, 116)',
                  'yellow': 'rgb(246, 207, 113)',
                  'darkgray': 'rgb(102, 102, 102)',
                  'lightgray': 'rgb(204, 204, 204)',
                  'red': 'rgb(251, 128, 114)'}

    clrred = color_dict.get('red')  # 'rgb(204,102,119)'
    clrgrn = color_dict.get('green')
    colorlimit = data[data.columns[0]].apply(lambda x: clrred if x >= 0.15 else clrgrn)
    data.fillna(0, inplace=True)

    # PLOT
    fig = px.bar(data_frame=data,
                 y=show_cols,
                 x=data.index,
                 template='gridon',
                 color_discrete_sequence=[clrgrn, clrred],
                 hover_name=data.index,
                 height=config.G2_HEIGHT)

    intra_day_mape = data[data.columns[0]].mean(skipna=True)

    # MAPE LINES
    fig.add_hline(y=intra_day_mape, line_width=1, line_dash="dash", line_color="darkorange", opacity=0.7,
                  annotation_text=f"MAPE: {round(intra_day_mape * 100, 1)}%",
                  annotation_position="top right", annotation=dict(font_size=14, font_family='Open Sans'))
    fig.update_layout(showlegend=False)
    fig.update_traces(marker_color=colorlimit)

    # TOOLTIP
    fig.update_traces(hovertemplate='<br> Time = %{x} <br>Error = %{y}')

    # X Axis
    fig.update_xaxes(  # tickangle=60,
        tickfont=dict(color=app_colors['text'], size=config.AXIS_TICK_SIZE),
        #gridcolor=app_colors['grid'],
        linecolor=app_colors['axis'],
        tickvals=data.index[::2])
    # Y Axis
    fig.update_yaxes(tickangle=0, tickfont=dict(color=app_colors['text'], size=config.AXIS_TICK_SIZE),
                     tickformat=".0%",
                     linecolor=app_colors['axis'],
                     #gridcolor=app_colors['grid']
                     )

    fig.update_layout(  # title_text=f"<b> Absolute Percentage Error : {select_state} - {date_string}<b>",
        title_x=0.5,
        xaxis_title=None,
        yaxis_title="% Error",
        legend_title=None,
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.95,
                    xanchor="right",
                    x=1),
        font=dict(size=config.GEN_FONT_GRAPHS,
                  color=app_colors['text']),
        hoverlabel=dict(bgcolor=app_colors['background'],
                        font_size=config.HOVER_SIZE),
        plot_bgcolor=app_colors['background'],
        paper_bgcolor=app_colors['background'],
        xaxis_tickformat='%H:%M')

    return fig


@app.callback(Output('showing-site', 'children'),
              Input('site-dropdown', 'value'))
def display_site_selected(site):
    if site is None:
        site = 'NR_Solar'
    return f"Site : {site}"


@app.callback(Output('showing-date', 'children'),
              Input('date-picker', 'date'))
def display_site_selected(date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A, %d %B %Y')
    return f"Date : {date}"


@app.callback(Output('updated-at', 'children'), [Input('interval-component', 'n_intervals')])
def update_dashboard_for_today(n):
    return [f'Dashboard updated at : {funcs.get_current_time()}']


app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True, host=config.HOST, port=config.PORT)
