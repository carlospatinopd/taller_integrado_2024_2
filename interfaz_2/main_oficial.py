from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import capturaDatos1  # Importamos el archivo capturaDatos.py
from firebase_admin import firestore
import threading

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

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

# Nueva ruta: Obtener los últimos dos ítems desde Firebase
@app.get("/items/ultimos/", response_model=List[dict])
def obtener_ultimos_items():
    # Obtener referencia del documento en Firestore
    try:
        doc_ref = capturaDatos1.db.collection("datos_test").document("datazos")
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            historico_datos = data.get("historico_datos", [])
            return historico_datos[-2:]  # Retornar los últimos dos datos
        else:
            raise HTTPException(status_code=404, detail="No se encontraron datos en Firebase")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectarse a Firebase: {str(e)}")

# Iniciar la captura de datos del puerto serial y enviarlos a Firebase
def iniciar_captura_datos():
    capturaDatos1.read_serial_data()

# Ejecutar la captura de datos en un hilo separado para que la API siga siendo accesible
captura_datos_thread = threading.Thread(target=iniciar_captura_datos, daemon=True)
captura_datos_thread.start()