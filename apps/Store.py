import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from scripts.utils import my_dash_components as mydbc
from app import app
from dash.dependencies import Input, Output
from data import run_query, engine
import plotly.express as px


# Lists to be displayed on the dropdown
city_lbl = ["CALI", "MEDELLIN"]
prod_cat_lbl = run_query(
    "select MIN(jerarquia_productos), nombre_cat from categorias group by "
    "nombre_cat",
    engine).dropna()
product_type = []
manufacturer = []

styles = {
    'container': {
        'position': 'fixed',
        'display': 'flex',
        'flex-direction': 'column',
        'height': 'auto',
        'width': '100%'
    }
}

content = html.Div(
    [
        dbc.Row([dbc.Col(html.H5("City Warehouse")),
                dbc.Col(html.H5("Category")),
                dbc.Col(html.H5("Manufacturer")),
                dbc.Col(html.H5("Subcategory")),
                 ]),
        # Dropdown with filters to plot the figure
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id="city",
                                     options=[{'label': i, 'value': i} for i in
                                              city_lbl],
                                    placeholder="Select a City Warehouse"
                                     ), width=3, style={'font-size': "80%"}),
                dbc.Col(dcc.Dropdown(id="product category", options=[
                    {'label': prod_cat_lbl.iloc[i]['nombre_cat'],
                     'value': prod_cat_lbl.iloc[i]['min']} for i in
                    range(prod_cat_lbl.shape[0])],
                    placeholder="Select a product category"), width=3, style={'font-size': "80%"}),
                dbc.Col(dcc.Dropdown(id="manufacturer",
                                     options=[product for product in manufacturer],
                                     placeholder="Select a manufacturer"), width=3, style={'font-size': "80%"}),
                dbc.Col(dcc.Dropdown(id="product sub-category",
                                     options=[product for product in product_type],
                                     placeholder="Select a product subcategory"), width=3, style={'font-size': "80%"})
            ]),
        dbc.Row(dbc.Col(html.H4("Date"))),
        dbc.Row([
                dbc.Col(dcc.DatePickerRange(id="my-date-picker-range",
                                            start_date="2020-01-07",
                                            end_date="2020-05-07",
                                            end_date_placeholder_text='Select a date!'
                                            ), style={'padding': 10, 'font-size': "50%"}),
                dbc.Col(html.P("Date on format Month/Day/Year"), style={"padding": 25}), dbc.Col(), dbc.Col()
                ]),
        dbc.Row([
            dbc.Col(dcc.Loading(id="loading-icon-g", children=dcc.Graph(id='store_graph'))),
            dbc.Col(dcc.Loading(id="loading-icon-s", children=dcc.Graph(id='storemoney_graph'))),

        ])
    ]
)

layout = html.Div(children=[
    mydbc.card(content=content, title="Store Analysis",
               description="Here you can find interesting data about Teaté's "
                           "associated stores."
                            "Please select the desired filters to plot the total quantity sold by stores and the total income that each store represents to Teaté",
               color="light", footer="")
], className="my-2")


@app.callback(Output('store_graph', 'figure'),
              [Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('city', 'value'),
               Input('manufacturer', 'value'),
               Input('product category', 'value'),
               Input('product sub-category', 'value')])
def update_graph(start_date, end_date, city, manufacturer, cat, sub_cat):
    """function to generate a store graph with the given inputs"""
    query = "select SUM(cantidad_pedido) as cantidad, t.Nombre_tienda from " \
            "historicopedidos h left join tiendas t on h.tienda = t.tienda " \
            "left join categorias c on h.Material = c.Material WHERE " \
            "Valor_TotalFactura >0 AND Fecha_Pedido >= " + "\'" + start_date\
            + "\'" + " AND Fecha_Pedido < " + "\'" + end_date + "\'" + ""

    if city is not None:
        if city == 'CALI':
            centro = 2000
        else:
            centro = 3000
        query = query + 'AND h.ce =' + str(centro)

    if manufacturer is not None:
        query = query + 'AND h.fabricante =' + str(manufacturer)

    if cat is not None:
        query = query + 'AND c.jerarquia_productos =' + str(cat)

    if sub_cat is not None:
        query = query + 'AND c.subcategoria =' + str(sub_cat)
    df = run_query(
        query + "group by t.Nombre_tienda, t.tienda order by cantidad DESC "
                "limit 10",
        engine)
    fig = px.bar(df, x='nombre_tienda', y='cantidad', title="Store Analysis", labels={'nombre_tienda':'Store name', 'cantidad': 'Quantity'})
    return fig


@app.callback(Output('storemoney_graph', 'figure'),
              [Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('city', 'value'),
               Input('manufacturer', 'value'),
               Input('product category', 'value'),
               Input('product sub-category', 'value')])
def update_moneygraph(start_date, end_date, city, manufacturer, cat, sub_cat):
    """function to generate a product income graph by store with the given inputs"""
    query = "select SUM(Valor_TotalFactura) as ventas, t.Nombre_tienda from " \
            "historicopedidos h left join tiendas t on h.tienda = t.tienda " \
            "left join categorias c on h.Material = c.Material WHERE " \
            "Valor_TotalFactura >0 AND Fecha_Pedido >= " + "\'" + start_date\
            + "\'" + " AND Fecha_Pedido < " + "\'" + end_date + "\'" + ""

    if city is not None:
        if city == 'CALI':
            centro = 2000
        else:
            centro = 3000
        query = query + 'AND h.ce =' + str(centro)

    if manufacturer is not None:
        query = query + 'AND h.fabricante =' + str(manufacturer)

    if cat is not None:
        query = query + 'AND c.jerarquia_productos =' + str(cat)

    if sub_cat is not None:
        query = query + 'AND c.subcategoria =' + str(sub_cat)
    df = run_query(
        query + "group by t.Nombre_tienda, t.tienda order by ventas DESC limit 10",
        engine)
    fig = px.bar(df, x='nombre_tienda', y='ventas', title="Income Analysis per Store", labels={'nombre_tienda':'Store name', 'ventas': 'Income'})
    return fig
