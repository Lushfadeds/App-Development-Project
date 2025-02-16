#import dash
#from dash import dcc, html
#import pandas as pd
#import plotly.express as px

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

sample_data = [
    {
        "day": 1,
        "products_sold": 120,
        "daily_sale": 600,
        "daily_customers": 50,
        "daily_unique_customers": 40,
        "money_spent_customer": 12,
        "expenses": 200,
        "labor_costs": 50.0,
        "energy_costs": 30.0
    },
    {
        "day": 2,
        "products_sold": 150,
        "daily_sale": 750,
        "daily_customers": 60,
        "daily_unique_customers": 50,
        "money_spent_customer": 12.5,
        "expenses": 220,
        "labor_costs": 55.0,
        "energy_costs": 32.0
    },
    {
        "day": 3,
        "products_sold": 130,
        "daily_sale": 650,
        "daily_customers": 55,
        "daily_unique_customers": 45,
        "money_spent_customer": 11.8,
        "expenses": 210,
        "labor_costs": 52.0,
        "energy_costs": 31.0
    },
    {
        "day": 4,
        "products_sold": 140,
        "daily_sale": 700,
        "daily_customers": 58,
        "daily_unique_customers": 48,
        "money_spent_customer": 12.1,
        "expenses": 215,
        "labor_costs": 53.0,
        "energy_costs": 31.5
    },
    {
        "day": 5,
        "products_sold": 160,
        "daily_sale": 800,
        "daily_customers": 65,
        "daily_unique_customers": 55,
        "money_spent_customer": 12.3,
        "expenses": 230,
        "labor_costs": 57.0,
        "energy_costs": 33.0
    },
    {
        "day": 6,
        "products_sold": 170,
        "daily_sale": 850,
        "daily_customers": 70,
        "daily_unique_customers": 60,
        "money_spent_customer": 12.1,
        "expenses": 240,
        "labor_costs": 60.0,
        "energy_costs": 34.0
    },
    {
        "day": 7,
        "products_sold": 180,
        "daily_sale": 900,
        "daily_customers": 75,
        "daily_unique_customers": 65,
        "money_spent_customer": 12.0,
        "expenses": 250,
        "labor_costs": 62.0,
        "energy_costs": 35.0
    },
    {
        "day": 8,
        "products_sold": 140,
        "daily_sale": 700,
        "daily_customers": 58,
        "daily_unique_customers": 48,
        "money_spent_customer": 12.1,
        "expenses": 215,
        "labor_costs": 53.0,
        "energy_costs": 31.5
    },
    {
        "day": 9,
        "products_sold": 150,
        "daily_sale": 750,
        "daily_customers": 60,
        "daily_unique_customers": 50,
        "money_spent_customer": 12.5,
        "expenses": 220,
        "labor_costs": 55.0,
        "energy_costs": 32.0
    },
    {
        "day": 10,
        "products_sold": 130,
        "daily_sale": 650,
        "daily_customers": 55,
        "daily_unique_customers": 45,
        "money_spent_customer": 11.8,
        "expenses": 210,
        "labor_costs": 52.0,
        "energy_costs": 31.0
    }
]