import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

def create_dash_app(flask_app):

    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/'
    )

    dash_app.layout = html.Div([
        html.H1('HELLO NIGGAS')
    ])
