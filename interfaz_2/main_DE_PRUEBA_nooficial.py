
from fastapi import FastAPI, Request,  HTTPException
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

# Variable global para el hilo de captura de datos
captura_datos_thread = None
captura_datos_activa = False
captura_datos_pausada = False

# Ruta para obtener todos los ítems desde Firebase
@app.get("/items/", response_model=List[dict])
def obtener_items():
    # Obtener referencia del documento en Firestore
    try:
        doc_ref = capturaDatos1.db.collection("datos_test").document("datazos")
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            return data.get("historico_datos", [])
        else:
            raise HTTPException(status_code=404, detail="No se encontraron datos en Firebase")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectarse a Firebase: {str(e)}")

# Ruta para iniciar la captura de datos del puerto serial y enviarlos a Firebase
@app.post("/start_capture/")
def start_capture():
    global captura_datos_thread, captura_datos_activa, captura_datos_pausada

    if captura_datos_activa:
        raise HTTPException(status_code=400, detail="La captura de datos ya está en curso.")

    # Iniciar la captura de datos en un hilo separado
    captura_datos_activa = True
    captura_datos_pausada = False
    captura_datos_thread = threading.Thread(target=capturaDatos1.read_serial_data, daemon=True)
    captura_datos_thread.start()

    return {"message": "Captura de datos iniciada."}

# Ruta para detener la captura de datos
@app.post("/stop_capture/")
def stop_capture():
    global captura_datos_activa

    if not captura_datos_activa:
        raise HTTPException(status_code=400, detail="No hay captura de datos en curso.")

    # Detener la captura de datos
    captura_datos_activa = False
    capturaDatos1.stop_serial_read()  # Detener la lectura

    return {"message": "Captura de datos detenida."}

# Ruta para pausar/reanudar la captura de datos
@app.post("/pause_resume_capture/")
def pause_resume_capture():
    global captura_datos_pausada, captura_datos_activa

    if not captura_datos_activa:
        raise HTTPException(status_code=400, detail="No hay captura de datos en curso para pausar o reanudar.")

    captura_datos_pausada = not captura_datos_pausada
    if captura_datos_pausada:
        capturaDatos1.pause_serial_read()  # Pausar la lectura en capturaDatos.py
        return {"message": "Captura de datos pausada."}
    else:
        capturaDatos1.resume_serial_read()  # Reanudar la lectura en capturaDatos.py
        return {"message": "Captura de datos reanudada."}

# Ruta para borrar todos los datos de Firebase
@app.post("/clear_data/")
def clear_data():
    try:
        doc_ref = capturaDatos1.db.collection("datos_test").document("datazos")
        doc_ref.set({"historico_datos": []})  # Establecer el histórico de datos como una lista vacía
        return {"message": "Todos los datos han sido borrados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar los datos en Firebase: {str(e)}") 

# Crear la app Dash con una URL base específica
dash_app = Dash(__name__, requests_pathname_prefix="/dash/")

# Definir el layout de la app Dash
dash_app.layout = html.Div([
    html.H1("Gráficos en Tiempo Real"),
    
    # Intervalo de actualización en teimpo real de los gráficos
    dcc.Interval(id="interval-component", interval=5*1000, n_intervals=0),  # Se actualizan cada 5 segundos

    # Títulos y gráficos para cada sensor
    html.Div([
        #html.H2("Voltaje"),
        dcc.Graph(id="grafico-voltaje"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        #html.H2("Presión"),
        dcc.Graph(id="grafico-presion"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        #html.H2("Temperatura"),
        dcc.Graph(id="grafico-temperatura"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        #html.H2("Corriente"),
        dcc.Graph(id="grafico-corriente"),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        #html.H2("Volumen"),
        dcc.Graph(id="grafico-volumen"),
    ], style={"margin-bottom": "20px"}),
])


# Función para obtener datos de un sensor específico de Firebase ############ ESTO ARREGLAR!!!!!!!!!!!!!!!!!!!
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
    fig_voltaje = px.line(df_voltaje, x="Tiempo", y="Voltaje", title="Voltaje")
    fig_presion = px.line(df_presion, x="Tiempo", y="Presión", title="Presión")
    fig_temperatura = px.line(df_temperatura, x="Tiempo", y="Temperatura", title="Temperatura")
    fig_corriente = px.line(df_corriente, x="Tiempo", y="Corriente", title="Corriente")
    fig_volumen = px.line(df_volumen, x="Tiempo", y="Volumen", title="Volumen")

    return fig_voltaje, fig_presion, fig_temperatura, fig_corriente, fig_volumen

# Montar la app Dash en FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))


# Ruta para la página principal de FastAPI con el HTML separado
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})