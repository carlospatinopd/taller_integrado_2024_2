from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

# Inicialización de Firebase Firestore
cred = credentials.Certificate("proyecto-electrolisis-2024-v2-8a2294fe2b42.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Modelo de datos
class Data(BaseModel):
    corriente: float
    voltaje: float
    temperatura: float
    presion: float

# Ruta para obtener datos desde Firestore
@app.get("/data", response_model=Data)
def obtener_datos_firestore():
    # Update to match your Firestore path: 'datos_temp/datazos2'
    doc_ref = db.collection('datos_temp').document('datazos2')
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Datos no encontrados")

    datos = doc.to_dict()
    
    # Return the data
    return {
        "corriente": datos.get("Corriente", 0),
        "presion": datos.get("Presion", 0),
        "voltaje": datos.get("Voltaje", 0),
        "temperatura": datos.get("Temperatura", 0)
    }
