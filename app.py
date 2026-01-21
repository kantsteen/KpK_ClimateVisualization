from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

#test
df = pd.read_csv('NASA_GISTEMP.csv', skiprows=1)
df = df.replace('***', pd.NA)
for col in df.columns:
    if col != 'Year':
        df[col] = pd.to_numeric(df[col], errors='coerce')



external_stylesheets=[dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    dbc.Row([
        html.Div(children='My first app with data, Graph, and Controls', className="text-primary text-center fs-3")
]),


    dbc.Row([
        dbc.RadioItems(options=[{"label": x, "value": x} for x in ['J-D', 'D-N', 'DJF', 'MAM', 'JJA', 'SON']], 
                       value='J-D', 
                       inline=True,
                       id='radio-buttons-final')
]),


dbc.Row([
    dbc.Col([
        dag.AgGrid(
        rowData=df.to_dict('records'),
        columnDefs=[{"field": i} for i in df.columns]
        )
    ], width=6),

    dbc.Col([
        dcc.Graph(figure={}, id='my-first-graph-final')
    ], width=6),
]),
    
], fluid=True)


@callback(
    Output(component_id='my-first-graph-final', component_property='figure'),
    Input(component_id='radio-buttons-final', component_property='value')
)
def update_graph(col_chosen):
    fig = px.line(df, x='Year', y=col_chosen, markers=True)
    return fig


if __name__ == '__main__':
    app.run(debug = True)