import serial
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import time
# Firebase setup
cred = credentials.Certificate('proyecto-electrolisis-2024-v2-8a2294fe2b42.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Serial port setup
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
MAX_MEASUREMENTS = 20

# Function to send data to Firebase
def send_to_firebase(data):
    # Sending data to "datos_test" collection, "datazos" document
    doc_ref = db.collection("datos_test").document("datazos")
    doc = doc_ref.get()

    # Create a new entry with the incoming data
    new_entry = {
        "Voltaje": data['voltaje'],
        "Corriente": data['corriente'],
        "Temperatura": data['temperatura'],
        "Presion": data['presion'],
        "Fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # If the document already exists, update the existing array of data
    if doc.exists:
        existing_data = doc.to_dict().get("historico_temperaturas", [])
        existing_data.append(new_entry)

        # If the number of measurements exceeds MAX_MEASUREMENTS, reset the data
        if len(existing_data) > MAX_MEASUREMENTS:
            existing_data = [new_entry]
    else:
        # If the document doesn't exist, create a new array
        existing_data = [new_entry]

    # Update or create the document with the new data
    doc_ref.set({"historico_temperaturas": existing_data})

    # Sending real-time data to "datos_temp" collection, "datazos2" document
    doc_ref_temp = db.collection("datos_temp").document("datazos2")
    new_entry_temp = {
        "Voltaje": data['voltaje'],
        "Corriente": data['corriente'],
        "Temperatura": data['temperatura'],
        "Presion": data['presion'],
        "Fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    doc_ref_temp.set(new_entry_temp)

# Function to read data from serial
def read_serial_data():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:  # Increased timeout to 2 seconds
            print(f"Listening to serial port: {SERIAL_PORT}")
            while True:
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    try:
                        # Parse line as JSON
                        data = json.loads(line)

                        # Validate that all required keys are present
                        required_keys = ['voltaje', 'corriente', 'temperatura', 'presion']
                        if all(key in data for key in required_keys):
                            print(f"Voltaje: {data['voltaje']} V, Corriente: {data['corriente']} A, Temperatura: {data['temperatura']} °C, Presión: {data['presion']} atm")
                            
                            # Send parsed data to Firebase
                            send_to_firebase(data)
                            # time.sleep(1)
                        else:
                            print("Error: Missing one or more required keys in the data.")
                            print(f"Received: {line}")
                    except json.JSONDecodeError:
                        print("Error: Could not decode the JSON.")
                        print(f"Received: {line}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

if __name__ == "__main__":
    read_serial_data()