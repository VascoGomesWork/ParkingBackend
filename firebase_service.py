import serial
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore
import random # Para simular outros parques

# --- Configuração Principal ---
# ! Mude para a sua porta COM (Windows) ou /dev/tty... (Linux/Mac)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600
SERVICE_ACCOUNT_KEY = 'serviceAccountKey.json'
COLLECTION_NAME = u'parques'

# --- Configuração do Parque Real (a1) ---
# ! Altere estas coordenadas para a localização real do seu sensor "a1"
# (Vá ao Google Maps, clique com o botão direito e copie as coordenadas)
LATITUDE_A1 = 37.0194  # Exemplo: Coordenadas de Faro, Portugal
LONGITUDE_A1 = -7.9304 # Exemplo: Coordenadas de Faro, Portugal

# --- Configuração dos Parques Simulados (para o mapa) ---
# Coordenadas de exemplo perto do parque "a1" para simulação
MOCK_PARKS = {
    "a2": {"lat": 37.0190, "lon": -7.9300},
    "a3": {"lat": 37.0188, "lon": -7.9305},
    "a4": {"lat": 37.0192, "lon": -7.9310},
}
# -------------------------------------

print("A iniciar o serviço de monitorização de parques...")
db = None

try:
    # --- 1. Ligar ao Firebase ---
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Ligado ao Firebase com sucesso.")
    
    # --- 1b. Enviar dados estáticos (simulados) para o Firebase ---
    # Isto corre apenas uma vez no arranque para garantir que os parques simulados existem
    print("A atualizar/criar parques simulados...")
    for park_id, coords in MOCK_PARKS.items():
        doc_ref = db.collection(COLLECTION_NAME).document(park_id)
        # Escolhe um estado aleatório ("livre" ou "ocupado") no arranque
        simulated_status = random.choice([u'livre', u'ocupado'])
        doc_ref.set({
            u'estado': simulated_status,
            u'latitude': coords['lat'],
            u'longitude': coords['lon'],
            u'lastUpdate': firestore.SERVER_TIMESTAMP,
            u'simulado': True # Uma flag para sabermos que este é falso
        }, merge=True) # merge=True para não apagar se já existir
    print("Parques simulados estão na base de dados.")


    # --- 2. Ligar à Porta Serial (Arduino) ---
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Esperar 2s para a ligação estabilizar
    print(f"A ouvir a porta {SERIAL_PORT} a {BAUD_RATE} baud...")

    # --- 3. Loop Principal (Ler do Arduino, Escrever no Firebase) ---
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()

            if line:
                try:
                    data = json.loads(line)
                    
                    if data.get('parque_id') and data.get('estado'):
                        park_id = data['parque_id'] # Deverá ser "a1"
                        status = data['estado']

                        # Preparar a referência do documento para o parque REAL
                        doc_ref = db.collection(COLLECTION_NAME).document(park_id)

                        # Criar ou Atualizar o documento
                        doc_ref.set({
                            u'estado': status,
                            u'latitude': LATITUDE_A1,
                            u'longitude': LONGITUDE_A1,
                            u'lastUpdate': firestore.SERVER_TIMESTAMP,
                            u'simulado': False # Este é o sensor real
                        }, merge=True)
                        
                        print(f"Estado REAL atualizado: Parque {park_id} -> {status}")

                except json.JSONDecodeError:
                    print(f"Dado inválido (não-JSON) recebido do Arduino: {line}")
        
        except KeyboardInterrupt:
            print("\nO utilizador parou o serviço.")
            break
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            print("A tentar reconectar em 5 segundos...")
            time.sleep(5)

except serial.SerialException as e:
    print(f"Erro Crítico: Não foi possível abrir a porta {SERIAL_PORT}. {e}")
    print("Verifique o nome da porta e se o Monitor Serial da IDE do Arduino está fechado.")
except FileNotFoundError:
    print(f"Erro Crítico: Ficheiro da chave de serviço '{SERVICE_ACCOUNT_KEY}' não encontrado.")
    print("Por favor, descarregue a chave da consola Firebase e coloque-a na mesma pasta.")
except Exception as e:
    print(f"Erro crítico ao inicializar: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Porta serial fechada.")
    print("Serviço terminado.")