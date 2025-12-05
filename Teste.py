import serial
import requests
import time

API_URL = "https://api-tam.vercel.app/luz"
PORTA = "COM3"
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

while True:
    try:
        linha = arduino.readline().decode(errors="ignore").strip()
        
        if linha:
            print(f"Recebido do Arduino: {linha}")

        # Tenta converter para número
        try:
            valor = int(linha)
        except ValueError:
            continue  # ignora linhas inválidas

        print(f"Lido do Arduino: {valor}")

        # Envio com timeout para não bloquear
        requests.post(API_URL, json={"light_value": valor}, timeout=3)

    except Exception as e:
        print("Erro:", e)
        time.sleep(2)
