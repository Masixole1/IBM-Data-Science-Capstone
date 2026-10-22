
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
launch_sites = spacex_df["Launch Site"].unique()

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "SpaceX Launch Records Dashboard",
        style={"textAlign": "center", "fontSize": 32}
    ),

    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] +
                [{"label": site, "value": site}
                 for site in launch_sites],
        value="ALL",
        placeholder="Select a Launch Site",
        searchable=True,
        clearable=False
    ),

    html.Br(),

    html.Div([
        dcc.Graph(id="success-pie-chart")
    ]),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[0, 10000]
    ),

    html.Br(),

    html.Div([
        dcc.Graph(id="success-payload-scatter-chart")
    ])
])


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        successful = spacex_df[
            spacex_df["class"] == 1
        ]
        counts = successful.groupby(
            "Launch Site"
        ).size().reset_index(name="Success Count")

        return px.pie(
            counts,
            values="Success Count",
            names="Launch Site",
            title="Total Success Launches By Site"
        )

    filtered_df = spacex_df[
        spacex_df["Launch Site"] == entered_site
    ]

    counts = filtered_df["class"].value_counts().reset_index()
    counts.columns = ["class", "count"]

    return px.pie(
        counts,
        values="count",
        names="class",
        title=f"Total Success Launches for site {entered_site}"
    )


@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    ]
)
def get_scatter_chart(entered_site, payload):
    low, high = payload

    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site == "ALL":
        title = "Correlation between Payload and Success for all Sites"
    else:
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]
        title = f"Correlation between Payload and Success for {entered_site}"

    return px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
