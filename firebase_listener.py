import serial
import json
import time
import random
from firebase_admin import firestore
from database import db

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
COLLECTION_NAME = 'parques'

LATITUDE_A1 = 37.0194
LONGITUDE_A1 = -7.9304

MOCK_PARKS = {
    "a2": {"lat": 37.0190, "lon": -7.9300},
    "a3": {"lat": 37.0188, "lon": -7.9305},
    "a4": {"lat": 37.0192, "lon": -7.9310},
}

def setup_mock_parks():
    print("Atualizando parques simulados no Firebase...")
    for park_id, coords in MOCK_PARKS.items():
        doc_ref = db.collection(COLLECTION_NAME).document(park_id)
        simulated_status = random.choice(['livre', 'ocupado'])
        doc_ref.set({
            'estado': simulated_status,
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'lastUpdate': firestore.SERVER_TIMESTAMP,
            'simulado': True
        }, merge=True)
    print("Parques simulados configurados.")

def listen_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"A ouvir {SERIAL_PORT} a {BAUD_RATE} baud...")
        
        setup_mock_parks()

        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    park_id = data.get('parque_id')
                    estado = data.get('estado')

                    if park_id and estado:
                        doc_ref = db.collection(COLLECTION_NAME).document(park_id)
                        doc_ref.set({
                            'estado': estado,
                            'latitude': LATITUDE_A1,
                            'longitude': LONGITUDE_A1,
                            'lastUpdate': firestore.SERVER_TIMESTAMP,
                            'simulado': False
                        }, merge=True)
                        print(f"Parque {park_id} atualizado -> {estado}")

                except json.JSONDecodeError:
                    print(f"Dado inválido: {line}")

            except Exception as e:
                print(f"Erro no loop principal: {e}")
                time.sleep(5)

    except serial.SerialException as e:
        print(f"Erro ao abrir porta serial: {e}")

if __name__ == "__main__":
    listen_arduino()
