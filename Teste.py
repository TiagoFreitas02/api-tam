import serial
import requests
import time

API_LUZ_URL = "https://api-tam.vercel.app/luz"
API_LED_URL = "https://api-tam.vercel.app/led"
API_ESTADO_URL = "https://api-tam.vercel.app/estado"
PORTA = "COM3"
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

ultimo_estado = None

while True:
    try:
        # Lê dados do Arduino
        linha = arduino.readline().decode(errors="ignore").strip()
        if "," in linha:
            valor_str, led_str = linha.split(",")
            light_value = int(valor_str)
            led_state_arduino = led_str.lower() == "true"
            print(f"Luz: {light_value}, LED Arduino: {led_state_arduino}")

            # Envia valores para APIs
            requests.post(API_LUZ_URL, json={"light_value": light_value})
            requests.post(API_LED_URL, json={"led_state": led_state_arduino})

        # Consulta estado do LED na BD
        resp = requests.get(API_ESTADO_URL, timeout=5)
        resp_json = resp.json()
        estado_bd = bool(resp_json.get("led", False))  # força boolean

        # Envia comando se diferente do Arduino ou se nunca enviado
        if estado_bd != ultimo_estado:
            cmd = "LED_ON\n" if estado_bd else "LED_OFF\n"
            arduino.write(cmd.encode())
            print(f"Enviado comando para Arduino: {cmd.strip()}")
            ultimo_estado = estado_bd

        time.sleep(0.2)  # loop mais rápido

    except Exception as e:
        print("Erro:", e)
        time.sleep(2)
