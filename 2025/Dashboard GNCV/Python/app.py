import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Cargar datos
ventas = pd.read_csv("GNCV.csv")

# Cargar shapefile y simplificar geometría para reducir uso de memoria
mapa = gpd.read_file("COLOMBIA.shp")
mapa["geometry"] = mapa["geometry"].simplify(0.01, preserve_topology=True)  

# Convertir tipos
ventas["ANIO_VENTA"] = ventas["ANIO_VENTA"].astype(str)
ventas["MES_VENTA"] = ventas["MES_VENTA"].astype(str)
ventas["DIA_VENTA"] = ventas["DIA_VENTA"].astype(str)
ventas["CODIGO_MUNICIPIO_DANE"] = ventas["CODIGO_MUNICIPIO_DANE"].astype(str)


nombre_amigable = {
    "EDS_ACTIVAS": "EDS Activas",
    "NUMERO_DE_VENTAS": "Numero de Ventas",
    "VEHICULOS_ATENDIDOS": "Vehiculos Atendidos",
    "CANTIDAD_VOLUMEN_SUMINISTRADO": "Cantidad Volumen Suministrado"
}

# Diccionario de nombres de meses
meses_nombre = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}

# Proyectar geometría para centroides correctos
gdf_proj = mapa.to_crs(epsg=3857)
mapa["centroid"] = gdf_proj.centroid
mapa["lon"] = mapa["centroid"].x
mapa["lat"] = mapa["centroid"].y

# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    html.H1("Consulta de Ventas GNCV en Colombia", className="my-3"),
    dcc.Tabs([
        dcc.Tab(label="Contexto", children=[
            html.Br(),
            html.P("Este dashboard fue desarrollado para explorar visualmente los datos relacionados con la venta de Gas Natural Comprimido Vehicular (GNCV) en Colombia, extraídos del portal de datos abiertos del gobierno colombiano."),
            html.P("Incluye herramientas interactivas que permiten al usuario analizar diferentes variables relacionadas con las estaciones de servicio, el volumen suministrado y los vehículos atendidos, a través del tiempo y el espacio (departamentos).")
        ]),

        dcc.Tab(label="Resumen", children=[
            html.Br(),
            html.Pre(ventas.describe(include='all').to_string())
        ]),

        dcc.Tab(label="Histograma", children=[
            html.Br(),
            dcc.Dropdown(
                id='hist_variable',
                options=[{"label": v, "value": k} for k, v in nombre_amigable.items()],
                value="EDS_ACTIVAS"
            ),
            dcc.Slider(id='hist_bins', min=5, max=50, step=1, value=10),
            dcc.Graph(id='hist_plot')
        ]),

        dcc.Tab(label="Dispersión", children=[
            html.Br(),
            dcc.Dropdown(id='xvar', options=[{"label": v, "value": k} for k, v in nombre_amigable.items()], value="EDS_ACTIVAS"),
            dcc.Dropdown(id='yvar', options=[{"label": v, "value": k} for k, v in nombre_amigable.items()], value="NUMERO_DE_VENTAS"),
            dcc.Graph(id='scatter_plot')
        ]),

        dcc.Tab(label="Evolución Temporal", children=[
            html.Br(),
            dcc.Dropdown(id='evol_variable', options=[{"label": v, "value": k} for k, v in nombre_amigable.items()], value="CANTIDAD_VOLUMEN_SUMINISTRADO"),
            dcc.Checklist(id='evol_anio', options=[{"label": y, "value": y} for y in ventas.ANIO_VENTA.unique()], value=[ventas.ANIO_VENTA.unique()[0]]),
            dcc.Graph(id='evol_plot')
        ]),

        dcc.Tab(label="Mapa", children=[
            html.Br(),
            dcc.Dropdown(id='map_variable', options=[{"label": v, "value": k} for k, v in nombre_amigable.items()], value="NUMERO_DE_VENTAS"),
            dcc.Graph(id='map_plot')
        ])
    ])
])

@app.callback(Output("hist_plot", "figure"), Input("hist_variable", "value"), Input("hist_bins", "value"))
def update_hist(var, bins):
    fig = px.histogram(ventas, x=var, nbins=bins, title=f"Histograma de {nombre_amigable[var]}")
    return fig

@app.callback(Output("scatter_plot", "figure"), Input("xvar", "value"), Input("yvar", "value"))
def update_scatter(x, y):
    fig = px.scatter(ventas, x=x, y=y, title=f"Dispersión entre {nombre_amigable[x]} y {nombre_amigable[y]}")
    return fig

@app.callback(Output("evol_plot", "figure"), Input("evol_variable", "value"), Input("evol_anio", "value"))
def update_evolucion(var, anios):
    df = ventas[ventas.ANIO_VENTA.isin(anios)].copy()
    df["MES_VENTA"] = df["MES_VENTA"].apply(lambda x: f"{int(x):02d}")
    df["MES_NOMBRE"] = df["MES_VENTA"].map(meses_nombre)
    df["MES_NOMBRE"] = pd.Categorical(df["MES_NOMBRE"], categories=list(meses_nombre.values()), ordered=True)
    df_grouped = df.groupby(["ANIO_VENTA", "MES_NOMBRE"])[var].sum().reset_index()
    fig = px.line(df_grouped, x="MES_NOMBRE", y=var, color="ANIO_VENTA", markers=True, title=f"Evolución de {nombre_amigable[var]}")
    return fig

@app.callback(Output("map_plot", "figure"), Input("map_variable", "value"))
def update_map(var):
    df_mapa = ventas.groupby("DEPARTAMENTO")[var].sum().reset_index()
    df_mapa[var] = df_mapa[var].apply(lambda x: np.log(x + 1))
    gdf_plot = mapa.merge(df_mapa, left_on="DPTO_CNMBR", right_on="DEPARTAMENTO", how="left")
    fig = px.choropleth_mapbox(
        gdf_plot,
        geojson=gdf_plot.geometry.__geo_interface__,
        locations=gdf_plot.index,
        color=var,
        center={"lat": 4.5709, "lon": -74.2973},
        mapbox_style="carto-positron",
        zoom=4.5,
        hover_name="DPTO_CNMBR",
        color_continuous_scale="Plasma",
        title=f"Mapa logarítmico de {nombre_amigable[var]}"
    )
    return fig

server = app.server

if __name__ == '__main__':
    app.run(debug=True)
