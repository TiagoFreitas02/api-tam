from flask import Flask, request, jsonify, render_template 
import os
import psycopg2
import requests

app = Flask(__name__)

db_config = {
    'dbname': 'db2021153107',
    'user': 'a2021153107',
    'password':'a2021153107',
    'host': 'aid.estgoh.ipc.pt'
}

def save_light_value(light_value):
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO luz (valor) VALUES (%s)", (light_value,))
        return True
    except Exception as e:
        print(f"Erro ao guardar na BD: {e}")
        return False

def get_light_values():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT valor, data FROM luz ORDER BY id DESC") 
                results = cur.fetchall()
        return results  # agora devolve lista de (valor, timestamp)
    except Exception as e:
        print(f"Erro ao pesquisar na BD: {e}")
        return []
    
def save_led_state(state: bool):
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                # Atualiza o estado em vez de inserir
                cur.execute("UPDATE led SET estado = %s WHERE id = 1", (state,))
        return True
    except Exception as e:
        print(f"Erro ao atualizar estado do led na BD: {e}")
        return False



@app.route('/led', methods=['POST'])
def receber_led():
    data = request.get_json()
    led_state = data.get('led_state')

    if led_state is None:
        return jsonify({"status": "error", "message": "led_state não obtido"}), 400

    success = save_led_state(led_state)

    if success:
        return jsonify({"status": "ok", "led_state": led_state})
    else:
        return jsonify({"status": "error", "message": "Erro ao guardar na BD"}), 500


@app.route('/luz', methods=['POST'])
def receber_luz():
    data = request.get_json()
    light_value = data.get('light_value')

    if light_value is None:
        return jsonify({"status": "error", "message": "light_value não obtido"}), 400

    success = save_light_value(light_value)

    if success:
        return jsonify({"status": "ok", "light_value": light_value})
    else:
        return jsonify({"status": "error", "message": "Erro ao guardar na BD"}), 500




@app.route('/estado', methods=['GET'])
def comando_led():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT estado FROM led WHERE id = 1')
                result = cur.fetchone()

        estado = result[0]
        return jsonify({"led": estado})
    except Exception as e:
        print(f"Erro ao buscar comando do LED: {e}")
        return jsonify({"led": False, "error": "Falha no servidor"})




@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    try:
        # Lê estado atual
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT estado FROM led WHERE id = 1')
                result = cur.fetchone()
        
        estado_atual = result[0] if result else False
        novo_estado = not estado_atual

        # Atualiza BD
        sucesso = save_led_state(novo_estado)
        print("Atualizou BD:", sucesso)

        # Envia comando para Arduino imediatamente
        try:
            requests.post(ARDUINO_API_URL, json={"led": novo_estado}, timeout=2)
            print(f"Comando enviado para Arduino: {'LED_ON' if novo_estado else 'LED_OFF'}")
        except Exception as e:
            print("Erro ao enviar comando para Arduino:", e)

        valores = get_light_values()
        msg = f"LED {'ligado' if novo_estado else 'desligado'}"
        return render_template("luz.html", valores=valores, msg=msg)

    except Exception as e:
        print(f"Erro ao alternar LED: {e}")
        valores = get_light_values()
        return render_template("luz.html", valores=valores, msg="Erro ao alternar LED")



@app.route('/')
def mostrar_luz():
    valores = get_light_values()
    return render_template("luz.html", valores=valores)
 

if __name__ == '__main__':
    app.run(debug=True)

    