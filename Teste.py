import serial
import requests
import time

# URL da API (Vercel ou ngrok)
API_URL = "https://unfamiliarised-semiretired-damion.ngrok-free.dev/luz"

# Configuração da porta serial do Arduino
PORTA = "COM3"
BAUD = 9600

# Inicializa Arduino
try:
    arduino = serial.Serial(PORTA, BAUD, timeout=1)
    time.sleep(2)
    print("Arduino conectado com sucesso!")
except Exception as e:
    print("Erro ao abrir porta serial:", e)
    exit(1)

while True:
    try:
        linha = arduino.readline().decode(errors="ignore").strip()

        # Ignora linhas vazias
        if not linha:
            continue

        # Lê apenas linhas com prefixo VAL:
        if linha.startswith("VAL:"):
            valor = int(linha.replace("VAL:", ""))
            print(f"Lido do Arduino: {valor}")

            # Envio para API
            try:
                requests.post(API_URL, json={"light_value": valor}, timeout=3)
            except requests.RequestException as e:
                print("Erro ao enviar para API:", e)

    except Exception as e:
        print("Erro geral:", e)
        time.sleep(2)
