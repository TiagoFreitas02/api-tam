from flask import Flask
import os
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')

db_config = {
    'dbname': os.environ.get('DATABASE_NAME'),
    'user': os.environ.get('DATABASE_USER'),
    'password': os.environ.get('DATABASE_PASSWORD'),
    'host': os.environ.get('DATABASE_HOST')
}

@app.route('/')
def home():
    return 'Hello, GNUNO!'

@app.route('/luz', methods=['POST'])
def receber_luz():
    data = request.get_json()
    light_value = data.get('light_value')
    print(f"Valor recebido: {light_value}")
    return jsonify({"status": "ok", "light_value": light_value})