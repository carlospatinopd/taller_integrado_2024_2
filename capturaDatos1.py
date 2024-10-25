import serial
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Firebase setup
cred = credentials.Certificate('C:/Users/esepu/Documentos/Universidad/Taller_Integrado/proyecto-electrolisis-2024-v2-64a8f0928f67.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Serial port setup
SERIAL_PORT = 'COM6'
BAUD_RATE = 9600

# Max number of data in firebase
max_data = 10

# Function to send data to Firebase
def send_to_firebase(data):
    doc_ref = db.collection("datos_test").document("datazos")
    doc = doc_ref.get()

    # Create a new entry with the incoming data
    new_entry = {
        "Voltaje": f"{data['voltaje']} V",
        "Corriente": f"{data['corriente']} A",
        "Temperatura": f"{data['temperatura']} °C",
        "Presión": f"{data['presion']} atm",
        "Volumen": f"{data['volumen']} L",
        "Fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # If the document already exists, update the existing array of data
    if doc.exists:
        existing_data = doc.to_dict().get("historico_datos", [])
        existing_data.append(new_entry)

        # If there are 'max_data' or more entries, reset the data
        if len(existing_data) >= max_data:
            existing_data = [new_entry]
    else:
        # If the document doesn't exist, create a new array
        existing_data = [new_entry]

    # Update or create the document with the new data
    doc_ref.set({"historico_datos": existing_data})

# Function to read data from serial
def read_serial_data():
    R = 0.0821  # Ideal gas constant in atm·L/(mol·K)
    n = 1  # Assume 1 mol of gas

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print(f"Listening to serial port: {SERIAL_PORT}")
            while True:
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    try:
                        # Parse line as JSON
                        data = json.loads(line)

                        # Calculate volume using the ideal gas law: PV = nRT -> V = nRT / P
                        temperatura_kelvin = data['temperatura'] + 273.15  # Convert temperature to Kelvin
                        volumen = round((n * R * temperatura_kelvin) / data['presion'], 2)
                        data['volumen'] = volumen

                        print(f"Voltaje: {data['voltaje']} V, Corriente: {data['corriente']} A, Temperatura: {data['temperatura']} °C, Presión: {data['presion']} atm, Volumen: {data['volumen']} L")
                        
                        # Send parsed data to Firebase
                        send_to_firebase(data)
                    except json.JSONDecodeError:
                        print("Error: Could not decode the JSON.")
                        print(f"Received: {line}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

if __name__ == "__main__":
    read_serial_data()