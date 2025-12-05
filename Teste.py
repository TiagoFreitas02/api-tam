import serial
import requests
import time

API_URL = "https://api-tam.vercel.app/luz"
PORTA = "COM3"
BAUD = 9600

# Inicialização do Arduino
try:
    arduino = serial.Serial(port=PORTA, baudrate=BAUD, timeout=1)
    time.sleep(2)
    print("Arduino conectado com sucesso!")
except Exception as e:
    print("Erro ao abrir porta serial:", e)
    exit(1)

while True:
    try:
        linha = arduino.readline().decode(errors="ignore").strip()
        
        if not linha:
            continue

        print(f"Recebido do Arduino: {linha}")

        # Tenta converter para número
        try:
            valor = int(linha)
        except ValueError:
            time.sleep(0.1)
            continue  # ignora linhas inválidas

        print(f"Lido do Arduino: {valor}")

        # Envio com timeout para não bloquear
        try:
            requests.post(API_URL, json={"light_value": valor}, timeout=3)
        except requests.RequestException as e:
            print("Erro ao enviar para API:", e)

    except Exception as e:
        print("Erro geral:", e)
        time.sleep(2)
