from flask import Flask, request, jsonify, render_template
import os
import psycopg2
import serial  # para comunicação com o Arduino

app = Flask(__name__)

# Configuração do banco de dados
db_config = {
    'dbname': 'db2021153107',
    'user': 'a2021153107',
    'password':'a2021153107',
    'host': 'aid.estgoh.ipc.pt'
}

# Inicializa a comunicação com o Arduino
# Substitui 'COM3' pela porta correta do teu Arduino no Windows ou '/dev/ttyACM0' no Linux
arduino = serial.Serial('COM3', 9600, timeout=1)  

# Função para guardar valor na BD
def save_light_value(light_value):
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO luz (valor) VALUES (%s)", (light_value,))
        return True
    except Exception as e:
        print(f"Erro ao guardar na BD: {e}")
        return False

# Função para ir buscar os valores à BD
def get_light_values():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT valor, data FROM luz ORDER BY id DESC") 
                results = cur.fetchall()
        return results 
    except Exception as e:
        print(f"Erro ao pesquisar na BD: {e}")
        return []

# Rota para receber valores via POST
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

# Rota para mostrar tabela de valores
@app.route('/')
def mostrar_luz():
    valores = get_light_values()
    return render_template("luz.html", valores=valores)

# Rota para desligar LED
@app.route('/desliga_led', methods=['POST'])
def desliga_led():
    try:
        arduino.write(b'0')  # envia '0' para o Arduino desligar o LED
        return "LED desligado!", 200
    except Exception as e:
        return f"Erro ao desligar LED: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
