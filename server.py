import serial
import requests
import time
import psycopg2

API_URL = "https://api-tam.vercel.app/luz"
PORTA = "COM3"
BAUD = 9600

MIN_SEND_INTERVAL = 1.0

# Intervalo para verificar comandos LED da base de dados (segundos)
LED_CHECK_INTERVAL = 1.0

# Configuração da base de dados
DB_CONFIG = {
    "dbname": "db2021153107",
    "user": "a2021153107",
    "password": "a2021153107",
    "host": "aid.estgoh.ipc.pt",
}

# Variável global para o objeto Serial do Arduino, serve de ponte para com o Arduino (falar com ele)
arduino_serial = None

# Variável para guardar o último estado processado (detectar mudanças)
ultimo_estado_processado = None


def conectar_arduino(porta, baud):
    # Estabelece conexão com o Arduino via Serial.
    try:
        arduino = serial.Serial(
            porta, baud, timeout=0.1
        )  # Timeout curto para não bloquear
        time.sleep(2)  # Esperar Arduino reiniciar
        arduino.reset_input_buffer()  # Limpar buffer inicial
        print(f"Conectado ao arduino")
        return arduino
    except Exception as e:
        print(f"Falha: {e}")


def ler_valor_mais_recente(arduino):
    """
    Lê o valor MAIS RECENTE do buffer serial, ignorando os dados antigos.
    """
    ultimo_valor = None

    # Ler TODAS as linhas disponíveis no buffer, guardar apenas a última
    while arduino.in_waiting > 0:
        linha = arduino.readline().decode(errors="ignore").strip()
        if linha and linha.isdigit():
            ultimo_valor = int(linha)

    # Se buffer estava vazio, esperar pela próxima leitura do Arduino
    if ultimo_valor is None:
        linha = arduino.readline().decode(errors="ignore").strip()
        if linha and linha.isdigit():
            ultimo_valor = int(linha)

    return ultimo_valor


def enviar_para_api(valor):
    try:
        response = requests.post(
            API_URL, json={"light_value": valor}, timeout=10  # Timeout de 10 segundos
        )

        # se a resposta for 200 é porque correu tudo bem
        if response.status_code == 200:
            return True
        else:
            print(f"API respondeu: {response.json()}")
            return False
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        return False


def ler_estado_led_bd():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT estado FROM controlo_led LIMIT 1")
                result = cur.fetchone()
                if result:
                    return result[0]  # Retorna o INTEGER
        return None
    except Exception as e:
        print(f"Erro ao ler estado LED da BD: {e}")
        return None


# Os comandos podem ser "LED:AUTO", "LED:ON", "LED:OFF"
def enviar_comando_arduino(comando):
    try:
        if arduino_serial and arduino_serial.is_open:
            arduino_serial.write((comando + "\n").encode())
            time.sleep(0.1)  # Pequeno delay para Arduino ter tempo de
            return True
        return False
    except Exception as e:
        print(f"Erro ao enviar comando ao Arduino: {e}")
        return False


def verificar_e_processar_comando_led():
    global ultimo_estado_processado
    estado_int = ler_estado_led_bd()

    if estado_int is None:
        print("Li mal o estado do led")
        return  # Erro ao ler

    # Se o estado não mudou, não fazer nada
    if estado_int == ultimo_estado_processado:
        return

    # Mapear INTEGER para comando Serial
    # 0 = auto, 1 = on, 2 = off

    sucesso = False
    if estado_int == 0:
        sucesso = enviar_comando_arduino("LED:AUTO")
    elif estado_int == 1:
        sucesso = enviar_comando_arduino("LED:ON")
    else:
        sucesso = enviar_comando_arduino("LED:OFF")


    # Enviar comando ao Arduino
    if sucesso:
        print(f"Comando LED enviado: {estado_int}")
        # Guardar estado processado
        ultimo_estado_processado = estado_int
    else:
        print(f"Falha ao enviar comando LED: {estado_int}")


def main():
    print("Boa tarde a tpods!")
    global arduino_serial, ultimo_estado_processado
    # Tentar detectar automaticamente ou usar configuração
    porta_usar = PORTA
    arduino_serial = conectar_arduino(porta_usar, BAUD)
    if arduino_serial is None:
        print("Arduino nao conectado")
        return

    estado_inicial = ler_estado_led_bd()
    if estado_inicial is not None:
        ultimo_estado_processado = estado_inicial
        print(
            f"Estado LED inicial: {ultimo_estado_processado} (0=auto, 1=on, 2=off)"
        )

    ultimo_envio = 0
    ultima_verificacao_led = 0

    while True:
        agora = time.time()

        try:
            # Verificar comandos LED da base de dados periodicamente
            # para garantir que o codigo tem o estado da LED correto
            if agora - ultima_verificacao_led >= LED_CHECK_INTERVAL:
                verificar_e_processar_comando_led()
                ultima_verificacao_led = agora

            # Ler o valor MAIS RECENTE (apaga dados antigos)
            # Isto tira o delay do arduino
            valor = ler_valor_mais_recente(arduino_serial)

            if valor is not None:
                #   Não enviar com muita freq
                if agora - ultimo_envio >= MIN_SEND_INTERVAL:
                    # Tentar enviar para a API
                    if enviar_para_api(valor):
                        print(
                            f"Luz: {valor} - Enviado para a base de dados"
                        )
                    else:
                        print(
                            f"Luz: {valor} - Falhou a enviar"
                        )

                    ultimo_envio = agora

        except Exception as e:
            print("Falhou", e)
            return


if __name__ == "__main__":
    main()