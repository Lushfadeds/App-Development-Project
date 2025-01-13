# dashboards.py
from __init__ import app, db, Stats
import pandas as pd
import plotly.express as px
from dash import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

dash_app.layout = html.Div([
    dcc.Graph(id='sales-graph'),
    html.Button('Create New Graph', id='create-graph-button'),
    html.Button('Delete Graph', id='delete-graph-button'),
    dcc.Input(id='update-graph-input', type='text', placeholder='Update Graph details')
])

@dash_app.callback(
    Output('sales-graph', 'figure'),
    [Input('create-graph-button', 'n_clicks')]
    )
def update_graph(n_clicks):
    graph = Stats.query.all()
    graph_data = [{'products_sold': s.products_sold, 'daily_sale': s.daily_sale, 'daily_customers': s.daily_customers, 'daily_unique_customers': s.daily_unique_customers, 'money_spent_customer': s.money_spent_customer} for s in graph]
    df = pd.DataFrame(graph_data)
    fig = px.bar(df, x='product', y='quantity')
    return fig

if __name__ == '__main__':
    dash_app.run_server(debug=True)
