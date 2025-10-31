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

@app.route('/about')
def about():
    try:
        # Conecta ao banco
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Executa um SELECT
        cursor.execute("SELECT nome, email FROM utilizadores LIMIT 5;")

        # Busca os resultados
        resultados = cursor.fetchall()

        # Monta uma string simples para exibir
        html = "<h1>Utilizadores</h1><ul>"
        for nome, email in resultados:
            html += f"<li>{nome} — {email}</li>"
        html += "</ul>"

        return html

    except Exception as e:
        return f"Erro ao acessar o banco: {e}"

    finally:
        # Fecha conexão
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()