import serial
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import threading
import time
import csv

# Firebase setup
cred = credentials.Certificate('C:/Users/esepu/Documentos/Universidad/Taller_Integrado/proyecto-electrolisis-2024-v2-64a8f0928f67.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Serial port setup
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600

# Flags para detener y pausar la lectura
stop_reading = False
pause_reading = False

# Lock para manejar la sincronización al pausar y reanudar
pause_lock = threading.Lock()

# Timestamp para controlar el intervalo de captura
timestamp_last_read = 0
interval_seconds = 1

# Declarar la conexión serial como una variable global
ser = None

# Function to send data to Firebase
def send_to_firebase(data):
    doc_ref = db.collection("datos_test").document("datazos")
    doc = doc_ref.get()

    new_entry = {
        "Voltaje": f"{data['voltaje']} V",
        "Corriente": f"{data['corriente']} A",
        "Temperatura": f"{data['temperatura']} °C",
        "Presión": f"{data['presion']} atm",
        "Volumen": f"{data['volumen']} L",
        "Fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    if doc.exists:
        existing_data = doc.to_dict().get("historico_datos", [])
        existing_data.append(new_entry)
    else:
        existing_data = [new_entry]

    doc_ref.set({"historico_datos": existing_data})

# Function to open serial connection
def open_serial_connection():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening to serial port: {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

# Function to close serial connection
def close_serial_connection():
    global ser
    if ser and ser.is_open:
        ser.close()
        print("Puerto serial cerrado.")

# Function to read data from serial
def read_serial_data():
    global stop_reading, pause_reading, timestamp_last_read, ser
    stop_reading = False
    pause_reading = False
    R = 0.0821  # Constante de gas ideal en atm·L/(mol·K)
    n = 1  # Supone 1 mol de gas
    timestamp_last_read = time.time()  # Inicializar el timestamp

    open_serial_connection()  # Intentar abrir la conexión al iniciar

    while not stop_reading:
        with pause_lock:
            if pause_reading:
                print("Lectura en pausa...")
                close_serial_connection()  # Cerrar el puerto serial al pausar
                time.sleep(1)  # Esperar un poco antes de seguir verificando
                continue

        # Intentar leer datos solo si el puerto serial está abierto
        if ser and ser.is_open:
            current_time = time.time()
            if current_time - timestamp_last_read >= interval_seconds:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        try:
                            data = json.loads(line)
                            temperatura_kelvin = float(data['temperatura']) + 273.15
                            volumen = round((n * R * temperatura_kelvin) / data['presion'], 2)
                            data['volumen'] = volumen

                            print(f"Voltaje: {data['voltaje']} V, Corriente: {data['corriente']} A, Temperatura: {data['temperatura']} °C, Presión: {data['presion']} atm, Volumen: {data['volumen']} L")

                            send_to_firebase(data)
                            timestamp_last_read = current_time  # Actualizar el timestamp después de una lectura exitosa
                        except json.JSONDecodeError:
                            print("Error: Could not decode the JSON.")
                            print(f"Received: {line}")
                except serial.SerialException as e:
                    print(f"Error reading from serial port: {e}")
            time.sleep(0.1)  # Pausa breve para evitar un bucle excesivamente rápido

    # Asegurarse de cerrar la conexión serial al detener la lectura
    close_serial_connection()

# Function to stop reading data from serial
def stop_serial_read():
    global stop_reading
    stop_reading = True

# Function to pause reading data from serial
def pause_serial_read():
    global pause_reading
    pause_reading = True

# Function to resume reading data from serial
def resume_serial_read():
    global pause_reading, timestamp_last_read
    pause_reading = False
    timestamp_last_read = time.time()  # Reiniciar el timestamp para evitar lecturas acumuladas
    open_serial_connection()  # Reabrir la conexión serial al reanudar