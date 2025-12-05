import serial
import requests
import time
import threading

# URLs da API
API_LUZ_URL = "https://api-tam.vercel.app/luz"
API_LED_URL = "https://api-tam.vercel.app/led"
API_ESTADO_URL = "https://api-tam.vercel.app/estado"
ARDUINO_API_URL = "http://127.0.0.1:5001/set_led"


# Configurações do Arduino
PORTA = "COM3"
BAUD = 9600

# Inicializa Arduino
arduino = serial.Serial(PORTA, BAUD, timeout=0.1)
time.sleep(2)

# Variáveis globais
light_value = 0
led_state_arduino = False
estado_bd = False
ultimo_estado = None

# -----------------------------
# Thread para leitura do Arduino
# -----------------------------
def ler_arduino():
    global light_value, led_state_arduino
    buffer = ""
    while True:
        try:
            # Lê bytes disponíveis
            data = arduino.read(arduino.in_waiting or 1).decode(errors="ignore")
            buffer += data

            # Processa linhas completas
            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)
                linha = linha.strip()
                if "," in linha:
                    valor_str, led_str = linha.split(",")
                    light_value = int(valor_str)
                    led_state_arduino = led_str.lower() == "true"
        except Exception as e:
            print("Erro na leitura do Arduino:", e)
        time.sleep(0.01)  # loop rápido para não perder dados

# -----------------------------
# Thread para atualizar a BD
# -----------------------------
def atualizar_bd():
    global ultimo_estado, estado_bd
    while True:
        try:
            # 1️⃣ Envia dados do Arduino para a API
            requests.post(API_LUZ_URL, json={"light_value": light_value})
            requests.post(API_LED_URL, json={"led_state": led_state_arduino})

            # 2️⃣ Consulta o estado do LED na BD
            resp = requests.get(API_ESTADO_URL, timeout=3)
            estado_bd = resp.json().get("led", False)

            # 3️⃣ Envia comando ao Arduino se necessário
            if estado_bd != ultimo_estado:
                cmd = "LED_ON\n" if estado_bd else "LED_OFF\n"
                arduino.write(cmd.encode())
                ultimo_estado = estado_bd

            time.sleep(0.2)  # atualização periódica
        except Exception as e:
            print("Erro na atualização da BD:", e)
            time.sleep(1)

# -----------------------------
# Thread para prints em tempo real
# -----------------------------
def mostrar_status():
    while True:
        print(f"Luz: {light_value}, LED Arduino: {led_state_arduino}, Estado BD: {estado_bd}")
        time.sleep(1)

# -----------------------------
# Inicializa threads
# -----------------------------
threading.Thread(target=ler_arduino, daemon=True).start()
threading.Thread(target=atualizar_bd, daemon=True).start()
threading.Thread(target=mostrar_status, daemon=True).start()

# Mantém o programa principal ativo
while True:
    time.sleep(1)
