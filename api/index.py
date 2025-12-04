from flask import Flask, request, jsonify, render_template 
import os
import psycopg2

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
                cur.execute("INSERT INTO led (estado) VALUES (%s)", (state,))
        return True
    except Exception as e:
        print(f"Erro ao guardar estado do led na BD: {e}")
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
                # Pega o último estado do LED
                cur.execute('SELECT estado FROM led ORDER BY id DESC LIMIT 1')
                result = cur.fetchone()

        estado = result[0] if result else False
        return jsonify({"led": estado})
    except Exception as e:
        print(f"Erro ao buscar comando do LED: {e}")
        return jsonify({"led": False, "error": "Falha no servidor"})



@app.route('/desliga_led', methods=['POST'])
def desliga_led():
    try:
        # 1️⃣ Pegar o último estado do LED
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT estado FROM led ORDER BY id DESC LIMIT 1')
                result = cur.fetchone()

        if result and result[0]:  # Se o LED está ligado
            # 2️⃣ Inserir False na tabela LED para desligar
            save_led_state(False)
            message = "LED desligado."
        else:
            message = "LED já estava desligado."

        # 3️⃣ Redireciona de volta à página principal
        valores = get_light_values()
        return render_template("luz.html", valores=valores, msg=message)

    except Exception as e:
        print(f"Erro ao desligar LED: {e}")
        valores = get_light_values()
        return render_template("luz.html", valores=valores, msg="Erro ao desligar LED")



@app.route('/')
def mostrar_luz():
    valores = get_light_values()
    return render_template("luz.html", valores=valores)
 

if __name__ == '__main__':
    app.run(debug=True)

    