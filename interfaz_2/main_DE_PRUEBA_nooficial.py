
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Dict
import capturaDatos1  
from firebase_admin import firestore
import threading

# Dash y WSGIMiddleware para la visualización de los graficos:
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from starlette.middleware.wsgi import WSGIMiddleware
import pandas as pd

# Inicializar la aplicación FastAPI
app = FastAPI()

# Configuración de la plantilla HTML
templates = Jinja2Templates(directory="templates")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Crear la app Dash con una URL base específica
dash_app = Dash(__name__, requests_pathname_prefix="/dash/")

# Definir el layout de la app Dash
dash_app.layout = html.Div([
    html.H1("Gráficos en Tiempo Real"),
    
    # Intervalo de actualización en teimpo real de los gráficos
    dcc.Interval(id="interval-component", interval=5*1000, n_intervals=0),  # Se actualizan cada 5 segundos

    # Títulos y gráficos para cada sensor
    html.Div([
        html.H2("Voltaje en Tiempo Real"),
        dcc.Graph(id="grafico-voltaje"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.H2("Presión en Tiempo Real"),
        dcc.Graph(id="grafico-presion"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.H2("Temperatura en Tiempo Real"),
        dcc.Graph(id="grafico-temperatura"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.H2("Corriente en Tiempo Real"),
        dcc.Graph(id="grafico-corriente"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.H2("Volumen en Tiempo Real"),
        dcc.Graph(id="grafico-volumen"),
    ], style={"margin-bottom": "20px"}),
])


# Función para obtener datos de un sensor específico de Firebase
def obtener_datos_sensor(sensor):
    try:
        # Obtener los datos de Firebase
        doc_ref = capturaDatos1.db.collection("datos_test").document("datazos")
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict().get("historico_datos", [])
            # Crear DataFrame para procesar los datos
            df = pd.DataFrame(data)
            return df[["timestamp", sensor]]
        else:
            return pd.DataFrame(columns=["timestamp", sensor])
    except Exception as e:
        print(f"Error al conectarse a Firebase: {e}")
        return pd.DataFrame(columns=["timestamp", sensor])

# Crear callbacks para actualizar cada gráfico con los datos en tiempo real
@dash_app.callback(
    Output("grafico-voltaje", "figure"),
    Output("grafico-presion", "figure"),
    Output("grafico-temperatura", "figure"),
    Output("grafico-corriente", "figure"),
    Output("grafico-volumen", "figure"),
    Input("interval-component", "n_intervals")
)
def actualizar_graficos(n):
    # Obtener datos de cada sensor desde Firebase
    df_voltaje = obtener_datos_sensor("Voltaje")
    df_presion = obtener_datos_sensor("Presión")
    df_temperatura = obtener_datos_sensor("Temperatura")
    df_corriente = obtener_datos_sensor("Corriente")
    df_volumen = obtener_datos_sensor("Volumen")

    # Crear gráficos para cada sensor
    fig_voltaje = px.line(df_voltaje, x="timestamp", y="Voltaje", title="Voltaje en Tiempo Real")
    fig_presion = px.line(df_presion, x="timestamp", y="Presión", title="Presión en Tiempo Real")
    fig_temperatura = px.line(df_temperatura, x="timestamp", y="Temperatura", title="Temperatura en Tiempo Real")
    fig_corriente = px.line(df_corriente, x="timestamp", y="Corriente", title="Corriente en Tiempo Real")
    fig_volumen = px.line(df_volumen, x="timestamp", y="Volumen", title="Volumen en Tiempo Real")

    return fig_voltaje, fig_presion, fig_temperatura, fig_corriente, fig_volumen

# Montar la app Dash en FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))


# Ruta para la página principal de FastAPI con el HTML separado
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})