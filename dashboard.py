import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

#def create_dash_app(flask_app):
#    dash_app = dash.Dash(
#        'test_line_graph',
#        server=app,
#        url_base_pathname='/dash/',
#    )
#
#    # Sample data for the line graph
#    data = pd.DataFrame({
#        'X': [1, 2, 3, 4],
#        'Y1': [10, 15, 13, 17],
#        'Y2': [16, 5, 11, 9]
#    })
#
#    # Create a line graph using Plotly Express
#    fig = px.line(
#        data,
#        x='X',
#        y=['Y1', 'Y2'],
#        labels={'X': 'X Axis', 'value': 'Y Axis'},
#        title='Sample Line Graph'
#    )
#
#    # Dash layout
#    dash_app.layout = html.Div([
#        dcc.Graph(id='line-graph', figure=fig)
#    ])