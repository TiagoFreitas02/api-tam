from flask import Flask, request, jsonify, render_template
import serial
import psycopg2
import time


app = Flask(__name__)

db_config = {
    'dbname': 'db2021153107',
    'user': 'a2021153107',
    'password':'a2021153107',
    'host': 'aid.estgoh.ipc.pt'
}

try:
    arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)
    time.sleep(2)
    print("Arduino conectado com sucesso!")
except Exception as e:
    print("Erro ao abrir a porta serial:", e)
    arduino = None

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
        return results
    except Exception as e:
        print(f"Erro ao pesquisar na BD: {e}")
        return []

@app.route('/luz', methods=['POST'])
def receber_luz():
    data = request.get_json()
    light_value = data.get('light_value')

    if light_value is None:
        return jsonify({"status": "error", "message": "light_value não obtido"}), 400

    success = save_light_value(light_value)
    return jsonify({"status": "ok", "light_value": light_value}) if success else \
           jsonify({"status": "error", "message": "Erro ao guardar na BD"}), 500

@app.route('/led', methods=['POST'])
def controlar_led():
    data = request.get_json()
    if not data:
        return jsonify({"status": "erro", "msg": "Dados JSON não recebidos"}), 400

    estado = data.get("estado")
    if estado not in ["0", "1", "A"]:
        return jsonify({"status": "erro", "msg": "estado inválido"}), 400

    if arduino is None:
        return jsonify({"status": "erro", "msg": "Arduino não conectado"}), 500

    try:
        arduino.write(str(estado).encode('utf-8'))
        arduino.flush()
        return jsonify({"status": "ok", "estado": estado})
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro ao comunicar com Arduino: {e}"}), 500

@app.route('/')
def mostrar_luz():
    valores = get_light_values()
    return render_template("luz.html", valores=valores)

if __name__ == '__main__':
    # Mantém debug=True apenas localmente
    app.run(debug=True, port=5000, host='0.0.0.0')
