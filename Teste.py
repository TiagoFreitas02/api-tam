import serial
import requests
import time

API_LUZ_URL = "https://api-tam.vercel.app/luz"  # tabela luz
API_LED_URL = "https://api-tam.vercel.app/led"  # tabela led
PORTA = "COM3"  
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

while True:
    try:
        linha = arduino.readline().decode(errors="ignore").strip()
        
        # Verifica se a linha contém a vírgula
        if "," in linha:
            valor_str, led_str = linha.split(",")
            
            # Converte valor da luz para inteiro
            light_value = int(valor_str)
            
            # Converte estado do LED para boolean
            led_state = led_str.lower() == "true"
            
            print(f"Luz: {light_value}, LED: {led_state}")
            
            # Envia para as APIs separadas
            requests.post(API_LUZ_URL, json={"light_value": light_value})
            requests.post(API_LED_URL, json={"led_state": led_state})

    except Exception as e:
        print("Erro:", e)
        time.sleep(2)
