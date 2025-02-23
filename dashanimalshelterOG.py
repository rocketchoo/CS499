import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
from crud import AnimalShelter
import pandas as pd

# Initialize Dash app
app = dash.Dash(__name__)

# Connect to MongoDB using the CRUD module
shelter = AnimalShelter('aacuser', 'password')

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Grazioso Salvare Animal Shelter Dashboard"),

    # Grazioso Salvare logo
    html.Img(src='/assets/logo.png', style={'height':'10%', 'width':'10%'}),

    # Dropdown for selecting rescue type
    dcc.Dropdown(
        id='rescue-type-dropdown',
        options=[
            {'label': 'Water Rescue', 'value': 'Water Rescue'},
            {'label': 'Mountain or Wilderness Rescue', 'value': 'Mountain or Wilderness Rescue'},
            {'label': 'Disaster or Individual Tracking', 'value': 'Disaster or Individual Tracking'}
        ],
        placeholder="Select a Rescue Type"
    ),

    # Data table to display shelter animals
    dash_table.DataTable(
        id='animal-table',
        columns=[{"name": i, "id": i} for i in ["name", "breed", "age", "rescue_type", "location"]],
        page_size=10,
        style_table={'overflowX': 'auto'}
    ),

    # Geolocation chart
    dcc.Graph(id='geolocation-chart'),

    # Additional chart (e.g., age distribution by breed)
    dcc.Graph(id='other-chart'),
])

# Callback to update the data table based on the selected rescue type
@app.callback(
    Output('animal-table', 'data'),
    [Input('rescue-type-dropdown', 'value')]
)
def update_table(selected_rescue):
    query = {"rescue_type": selected_rescue} if selected_rescue else {}
    data = shelter.read(query)
    return pd.DataFrame(data).to_dict('records')

# Callback to update the geolocation chart based on the data table
@app.callback(
    Output('geolocation-chart', 'figure'),
    [Input('animal-table', 'data')]
)
def update_map(data):
    df = pd.DataFrame(data)
    if df.empty:
        return px.scatter_mapbox()
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon", hover_name="name",
        hover_data=["breed", "age"], zoom=10
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig

# Callback to update the additional chart based on the data table
@app.callback(
    Output('other-chart', 'figure'),
    [Input('animal-table', 'data')]
)
def update_other_chart(data):
    df = pd.DataFrame(data)
    if df.empty:
        return px.bar()
    fig = px.bar(df, x="breed", y="age", color="breed", title="Age Distribution by Breed")
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)