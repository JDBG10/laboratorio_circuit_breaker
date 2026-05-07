import os
import time
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_connection():
    """Reintenta la conexión a MySQL hasta 10 veces (el contenedor puede tardar en estar listo)."""
    for intento in range(1, 11):
        try:
            return mysql.connector.connect(
                host     = os.getenv("DB_HOST"),
                user     = os.getenv("DB_USER"),
                password = os.getenv("DB_PASSWORD"),
                database = os.getenv("DB_NAME")
            )
        except Exception as e:
            print(f"[usuarios] Intento {intento}/10: {e}", flush=True)
            time.sleep(3)
    raise Exception("No se pudo conectar a MySQL.")


@app.route("/")
def home():
    return "Servicio de usuarios funcionando"


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, correo, telefono, fecha_nac FROM usuarios")
    filas  = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": f[0], "nombre": f[1], "correo": f[2], "telefono": f[3], "fecha_nac": str(f[4])}
        for f in filas
    ])


@app.route("/usuarios/<int:id_usuario>", methods=["GET"])
def obtener_usuario(id_usuario):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, correo, telefono, fecha_nac FROM usuarios WHERE id = %s",
        (id_usuario,)
    )
    fila = cursor.fetchone()
    conn.close()
    if not fila:
        return jsonify({"error": f"Usuario {id_usuario} no encontrado"}), 404
    return jsonify({"id": fila[0], "nombre": fila[1], "correo": fila[2], "telefono": fila[3], "fecha_nac": str(fila[4])})


@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data   = request.json
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, telefono, fecha_nac) VALUES (%s, %s, %s, %s)",
        (data["nombre"], data["correo"], data["telefono"], data["fecha_nac"])
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensaje": "Usuario creado", "id": nuevo_id}), 201


@app.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
def eliminar_usuario(id_usuario):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
    conn.commit()
    afectados = cursor.rowcount
    conn.close()
    if afectados == 0:
        return jsonify({"error": f"Usuario {id_usuario} no encontrado"}), 404
    return jsonify({"mensaje": f"Usuario {id_usuario} eliminado"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
