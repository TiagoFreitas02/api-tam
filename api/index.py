from flask import Flask, request, render_template
import psycopg2
import serial
import time

app = Flask(__name__)

# --- Configurações do Banco ---
db_config = {
    'dbname': 'db2021153107',
    'user': 'a2021153107',
    'password':'a2021153107',
    'host': 'aid.estgoh.ipc.pt'
}

# --- Configuração Arduino ---
PORTA = "COM3"
BAUD = 9600
arduino = serial.Serial(PORTA, BAUD, timeout=1)
time.sleep(2)

# --- Funções de BD ---
def save_light_value(light_value):
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO luz (valor) VALUES (%s)", (light_value,))
        return True
    except Exception as e:
        print(f"Erro ao guardar luz: {e}")
        return False

def get_light_values():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT valor, data FROM luz ORDER BY id DESC")
                return cur.fetchall()
    except Exception as e:
        print(f"Erro ao ler luz: {e}")
        return []

def save_led_state(state: bool):
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE led SET estado = %s WHERE id = 1", (state,))
        return True
    except Exception as e:
        print(f"Erro ao atualizar LED: {e}")
        return False

def get_led_state():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT estado FROM led WHERE id = 1")
                result = cur.fetchone()
                return result[0] if result else False
    except Exception as e:
        print(f"Erro ao ler LED: {e}")
        return False

# --- Rotas Flask ---
@app.route('/')
def index():
    valores = get_light_values()
    led_estado = get_led_state()
    return render_template("luz.html", valores=valores, led_estado=led_estado, msg="")

@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT estado FROM led WHERE id = 1')
                result = cur.fetchone()
        
        estado_atual = result[0] if result else False
        novo_estado = not estado_atual  # alterna o estado

        # Atualiza o estado
        save_led_state(novo_estado)

        # Atualiza página
        valores = get_light_values()
        msg = f"LED {'ligado' if novo_estado else 'desligado'}"
        return render_template("luz.html", valores=valores, msg=msg)

    except Exception as e:
        print(f"Erro ao alternar LED: {e}")
        valores = get_light_values()
        return render_template("luz.html", valores=valores, msg="Erro ao alternar LED")

# --- Rota para receber valores do Arduino ---
@app.route('/luz', methods=['POST'])
def receber_luz():
    data = request.get_json()
    light_value = data.get('light_value')
    if light_value is not None:
        save_light_value(light_value)
        return {"status": "ok"}
    return {"status": "erro"}

# --- Rota para receber estado do LED do Arduino (opcional) ---
@app.route('/led', methods=['POST'])
def receber_led():
    data = request.get_json()
    led_state = data.get('led_state')
    if led_state is not None:
        save_led_state(led_state)
        return {"status": "ok"}
    return {"status": "erro"}

if __name__ == '__main__':
    app.run(debug=True)
