import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px

app = Dash(__name__)


styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}

data = pd.read_csv('flights.csv')
# data = data.query('day < 15 and and arr_delay < 200')
n_samples_per_day = 10
data = data.groupby('day').apply(lambda x: x.sample(n=min(len(x), n_samples_per_day))).reset_index(drop=True)
data = data.query(" arr_delay < 141")


min_day = data["day"].min()
max_day = data["day"].max()
all_day = data["day"].unique()

all_companies = data['name'].unique()

data_table_cols = [
    'id', 'day', 'arr_time', 'sched_arr_time', 'arr_delay',
    'distance', 'name'
]

n_clicks = 0
total_clicks = 0
app.layout = html.Div([
    html.H1("Flight analysis of airline companies", style={'textAlign': 'center'}),
    html.Div([
        dcc.Graph("histogram-with-slider", config={"displayModeBar": False}),
        dcc.Graph(id="scatter_plot"),
        dcc.Graph(id="sunburst_plot"),
        html.Label("Day range"),
        dcc.RangeSlider(
            id='day_range',
            min=min_day,
            max=max_day,
            value=(min_day, max_day),
            marks={str(day): str(day)
                   for day in all_day},

        ),
        html.Label("Company name"),
        dcc.Checklist(
            id="company_list",
            options=[{
                "label": i,
                "value": i
            } for i in all_companies],
            value=all_companies,
            labelStyle={'display': 'inline-block'}
        ),
        html.Hr(),
        html.Button("Reset selection", id='reset', n_clicks=0),
        html.H3(id="selected_count"),
        dash_table.DataTable(
            id="data-table",
            data=[],
            page_size=10,
            columns=[{
                'name': i,
                "id": i
            } for i in data_table_cols]
        )
    ]),
],
    style={"margin-bottom": "150px"}
)


@app.callback(
    Output("histogram-with-slider", "figure"),
    Output("scatter_plot", "figure"),
    Output("sunburst_plot", "figure"),
    Output("data-table", "data"),
    Output("selected_count", "children"),
    Input("day_range", 'value'),
    Input("company_list", 'value'),
    Input("scatter_plot", 'selectedData'),
    Input("reset", 'n_clicks')
)

def update_fiqure(day_range, company_list, selectedData, n_clicks):
    global total_clicks
    filtered_data = data[data["day"].between(day_range[0], day_range[1])
                         & data["name"].isin(company_list)]

    fig_hist = px.histogram(filtered_data, x='arr_delay', color='name', labels={'arr_delay': 'Arrival Delay'}, title='Arrival Delay Distribution')

    fig_scatter = px.scatter(
        filtered_data,
        x="day",
        y='arr_delay',
        labels={'arr_delay': 'Arrival Delay'},
        hover_data=["day", "name", "arr_delay", "arr_time"],
        custom_data=[filtered_data.index]
    )

    fig_sunburst = px.sunburst(filtered_data, path=['name', 'day', 'arr_delay'])

    fig_scatter.update_layout(clickmode="event+select", uirevision=True)
    fig_scatter.update_traces(selected_marker_color="red")

    if n_clicks > total_clicks:
        fig_scatter.update_traces(marker_color="blue")
        total_clicks = n_clicks
        selectedData = None

    if selectedData:
        points = selectedData['points']
        index_list = [p["customdata"][0] for p in points]

        filtered_data = data[data.index.isin(index_list)]
        num_points_label = f"showing {len(points)} selected points:"
    else:
        num_points_label = "No points selected - showing top 10 only"
        filtered_data = filtered_data.head(10)

    return fig_hist, fig_scatter, fig_sunburst, filtered_data.to_dict(
        "records"), num_points_label



if __name__ == "__main__":
    app.run_server(debug=True)

