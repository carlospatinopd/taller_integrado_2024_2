from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
#from datos import temp

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

# Modelo de datos
class Item(BaseModel):
    id: int
    nombre: str
    Valor: float
    descripcion: Optional[str] = None

# Simulación de base de datos
base_datos: List[Item] = [
    {"id": 1, "nombre": "humedad", "Valor": 55, "descripcion": "sensor 3"},
    {"id": 2, "nombre": "temp", "Valor": 45, "descripcion": "sensor 4"},
    {"id": 3, "nombre": "volataje", "Valor": 55, "descripcion": "sensor 5"}
]

# Rutas de la API
@app.get("/items/", response_model=List[Item])
def obtener_items():
    return base_datos

@app.post("/items/", response_model=Item)
def crear_item(item: Item):
    if any(x.id == item.id for x in base_datos):
        raise HTTPException(status_code=400, detail="El ID ya existe")
    base_datos.append(item)
    return item

@app.delete("/items/{item_id}", response_model=Item)
def eliminar_item(item_id: int):
    item = next((x for x in base_datos if x.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    base_datos.remove(item)
    return item

# Nueva ruta: Obtener los últimos dos ítems
@app.get("/items/ultimos/", response_model=List[Item])
def obtener_ultimos_items():
    return base_datos[-2:]  # Retorna los últimos dos ítems