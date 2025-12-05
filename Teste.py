import serial
import requests
import time
import threading

API_LUZ_URL = "https://api-tam.vercel.app/luz"
API_LED_URL = "https://api-tam.vercel.app/led"
API_ESTADO_URL = "https://api-tam.vercel.app/estado"
PORTA = "COM3"
BAUD = 9600

arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

ultimo_estado = None
estado_bd = False
led_state_arduino = False
light_value = 0

def ler_arduino():
    global light_value, led_state_arduino
    while True:
        linha = arduino.readline().decode(errors="ignore").strip()
        if "," in linha:
            valor_str, led_str = linha.split(",")
            light_value = int(valor_str)
            led_state_arduino = led_str.lower() == "true"

def atualizar_bd():
    global ultimo_estado, estado_bd
    while True:
        try:
            # Envia dados do Arduino
            requests.post(API_LUZ_URL, json={"light_value": light_value})
            requests.post(API_LED_URL, json={"led_state": led_state_arduino})

            # Consulta estado do LED
            resp = requests.get(API_ESTADO_URL, timeout=5)
            estado_bd = resp.json().get("led", False)

            # Envia comando ao Arduino se necessário
            if estado_bd != ultimo_estado:
                cmd = "LED_ON\n" if estado_bd else "LED_OFF\n"
                arduino.write(cmd.encode())
                print(f"Enviado comando para Arduino: {cmd.strip()}")
                ultimo_estado = estado_bd

            time.sleep(0.5)  # menos delay
        except Exception as e:
            print("Erro:", e)
            time.sleep(1)

# Threads separadas
threading.Thread(target=ler_arduino, daemon=True).start()
threading.Thread(target=atualizar_bd, daemon=True).start()

while True:
    print(f"Luz: {light_value}, LED Arduino: {led_state_arduino}, Estado BD: {estado_bd}")
    time.sleep(1)
