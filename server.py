import serial
import requests
import time

API_URL = "https://api-tam.vercel.app/luz"
PORTA = "COM3"  
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD,timeout=1)
time.sleep(2)

while True:
    try:
        linha = arduino.readline().decode(errors="ignore").strip()
        if linha.isdigit():
            valor = int(linha)
            print(f"Lido do Arduino: {valor}")
            requests.post(API_URL, json={"light_value": valor})
    except Exception as e:
        print("Erro:", e)
        time.sleep(2)  