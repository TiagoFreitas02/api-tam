from flask import Flask, request, jsonify, render_template  # render_template adicionado para HTML
import os
import psycopg2

app = Flask(__name__)

db_config = {
    'dbname': os.environ.get('DATABASE_NAME'),
    'user': os.environ.get('DATABASE_USER'),
    'password': os.environ.get('DATABASE_PASSWORD'),
    'host': os.environ.get('DATABASE_HOST')
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
                cur.execute("SELECT valor FROM luz ORDER BY id DESC") 
                results = cur.fetchall()
        return [r[0] for r in results]
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

    if success:
        return jsonify({"status": "ok", "light_value": light_value})
    else:
        return jsonify({"status": "error", "message": "Erro ao guardar na BD"}), 500


@app.route('/luz_html')
def mostrar_luz():
    valores = get_light_values()  
    return render_template("luz.html", valores=valores) 

if __name__ == '__main__':
    app.run(debug=True)
