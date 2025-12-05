from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

db_config = {
    "dbname": "db2021153107",
    "user": "a2021153107",
    "password": "a2021153107",
    "host": "aid.estgoh.ipc.pt",
}

# Número máximo de registos a mostrar no histórico
linhas_mostradas = 50


def get_db_connection():
    """Cria uma nova conexão com a base de dados.
    IMPORTANTE: Sempre usar com 'with' para garantir que a conexão é fechada."""
    return psycopg2.connect(**db_config)


def guardar_valor_de_luz(valor_de_luz):
    try:
        # Usar 'with' garante que a conexão é fechada automaticamente
        with get_db_connection() as connection:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO luz (valor) VALUES (%s)", (valor_de_luz,))
            connection.commit()
        return True
    except Exception as e:
        print(f"Erro ao guardar na BD: {e}")
        return False


def get_valores_de_luz(limit=linhas_mostradas):
    try:
        # Usar 'with' garante que a conexão é fechada automaticamente
        with get_db_connection() as connection:
            with connection.cursor() as cur:
                # LIMIT para evitar carregar todos os registos (performance)
                cur.execute(
                    "SELECT valor, data FROM luz ORDER BY id DESC LIMIT %s", (limit,)
                )
                results = cur.fetchall()
        return results  # agora devolve lista de (valor, timestamp) ordenados por mais recente
    except Exception as e:
        print(f"Erro ao pesquisar na BD: {e}")
        return []


def atualizar_estado_led(estado_int):
    # Validar estado (deve ser 0, 1 ou 2)
    if estado_int not in [0, 1, 2]:
        print(f"Estado LED inválido: {estado_int}. Deve ser 0, 1 ou 2.")
        return False

    try:
        # Usar 'with' garante que a conexão é fechada automaticamente
        with get_db_connection() as connection:
            with connection.cursor() as cur:
                # Verificar se existe registo
                cur.execute("SELECT COUNT(*) FROM controlo_led")
                count = cur.fetchone()[0]

                if count == 0:
                    # Inserir primeiro registo
                    cur.execute(
                        "INSERT INTO controlo_led (estado) VALUES (%s)", (estado_int,)
                    )
                else:
                    # Atualizar estado existente
                    cur.execute("UPDATE controlo_led SET estado = %s", (estado_int,))

            connection.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar estado LED: {e}")
        return False


@app.route("/luz", methods=["POST"])
def receber_luz():
    data = request.get_json()

    # Validação: verificar se dados foram recebidos
    if not data:
        return (
            jsonify({"status": "error", "message": "JSON inválido ou não recebido"}),
            400,
        )

    light_value = data.get("light_value")

    # Validação: verificar se light_value existe
    if light_value is None:
        return (
            jsonify(
                {"status": "error", "message": "Campo 'light_value' não encontrado"}
            ),
            400,
        )

    light_value = int(light_value)
        

    # Guardar na base de dados
    success = guardar_valor_de_luz(light_value)

    if success:
        return jsonify(
            {
                "status": "ok",
                "light_value": light_value,
                "message": "Valor guardado com sucesso",
            },
            200,
        )

    return (
        jsonify({"status": "error", "message": "Erro ao guardar na base de dados"}),
        500,
    )


@app.route("/")
def mostrar_luz():
    valores = get_valores_de_luz(limit=linhas_mostradas)
    return render_template("luz.html", valores=valores)


@app.route("/led", methods=["POST"])
def controlar_led():
    """Endpoint para controlar o LED. Recebe estado no 0=auto, 1=on, 2=off"""
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "JSON inválido"}), 400

    estado = data.get("estado")

    if estado is None:
        return (
            jsonify({"status": "error", "message": "Campo 'estado' não encontrado"}),
            400,
        )

    try:
        estado = int(estado)
        if estado not in [0, 1, 2]:
            return (
                jsonify({"status": "error", "message": "Estado deve ser 0, 1 ou 2"}),
                400,
            )
    except (ValueError, TypeError):
        return (
            jsonify(
                {"status": "error", "message": "Estado deve ser um número inteiro"}
            ),
            400,
        )

    if atualizar_estado_led(estado) == True:
        if estado == 0:
            return jsonify({ "message": "automatico" })
        if estado ==1:
            return jsonify({ "message": "ligado" })
        if estado ==2:
            return jsonify({ "message": "desligado" })
        else:
            return jsonify({"message": "invalido"})

    

    return (
        jsonify({"status": "error", "message": "Erro ao atualizar estado do LED"}),
        500,
    )


if __name__ == "__main__":
    print("Programa iniciado")
    app.run(debug=True)