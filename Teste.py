import serial
import requests
import time

API_LUZ_URL = "https://api-tam.vercel.app/luz"  # tabela luz
API_LED_URL = "https://api-tam.vercel.app/led"  # tabela led
API_ESTADO_URL = "https://api-tam.vercel.app/estado"  # endpoint do último estado
PORTA = "COM3"  
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

ultimo_estado = None  # para evitar enviar comando repetido

while True:
    try:
        # 1️⃣ Lê dados do Arduino
        linha = arduino.readline().decode(errors="ignore").strip()
        
        if "," in linha:
            valor_str, led_str = linha.split(",")
            light_value = int(valor_str)
            led_state_arduino = led_str.lower() == "true"
            
            print(f"Luz: {light_value}, LED: {led_state_arduino}")
            
            # 2️⃣ Envia valores para APIs
            requests.post(API_LUZ_URL, json={"light_value": light_value})
            requests.post(API_LED_URL, json={"led_state": led_state_arduino})

        # 3️⃣ Consulta o estado atual do LED na BD
        resp = requests.get(API_ESTADO_URL, timeout=5)
        resp_json = resp.json()
        estado_bd = resp_json.get("led", False)
        
        # 4️⃣ Se o estado na BD for diferente do Arduino, envia comando Serial
        if estado_bd != ultimo_estado:
            cmd = "LED_ON\n" if estado_bd else "LED_OFF\n"
            arduino.write(cmd.encode())
            ultimo_estado = estado_bd

    except Exception as e:
        print("Erro:", e)
        time.sleep(2)
