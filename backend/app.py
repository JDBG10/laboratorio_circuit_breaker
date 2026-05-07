import os
import time
import requests
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
            print(f"[backend] Intento {intento}/10: {e}", flush=True)
            time.sleep(3)
    raise Exception("No se pudo conectar a MySQL.")


@app.route("/")
def home():
    return "Backend de mascotas funcionando"


@app.route("/mascotas", methods=["GET"])
def listar_mascotas():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, tipo, raza, edad, id_usuario FROM mascotas")
    filas  = cursor.fetchall()
    conn.close()
    return jsonify({"mascotas": [
        {"id": f[0], "nombre": f[1], "tipo": f[2], "raza": f[3], "edad": f[4], "id_usuario": f[5]}
        for f in filas
    ]})


@app.route("/mascotas/<int:id_mascota>", methods=["GET"])
def obtener_mascota(id_mascota):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, tipo, raza, edad, id_usuario FROM mascotas WHERE id = %s",
        (id_mascota,)
    )
    fila = cursor.fetchone()
    conn.close()
    if not fila:
        return jsonify({"error": f"Mascota {id_mascota} no encontrada"}), 404
    return jsonify({"id": fila[0], "nombre": fila[1], "tipo": fila[2], "raza": fila[3], "edad": fila[4], "id_usuario": fila[5]})


@app.route("/mascotas", methods=["POST"])
def crear_mascota():
    data   = request.json
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mascotas (nombre, tipo, raza, edad, id_usuario) VALUES (%s, %s, %s, %s, %s)",
        (data["nombre"], data["tipo"], data["raza"], data["edad"], data.get("id_usuario", 1))
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensaje": "Mascota creada", "id": nuevo_id}), 201


@app.route("/relacion")
def relacion():
    """Mascotas enriquecidas con datos del dueño (consulta al servicio de usuarios)."""
    resp         = requests.get("http://usuarios:5000/usuarios", timeout=2)
    usuarios_map = {u["id"]: u for u in resp.json()}

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, tipo, raza, edad, id_usuario FROM mascotas")
    filas  = cursor.fetchall()
    conn.close()

    return jsonify({"relaciones": [
        {
            "mascota": {"id": f[0], "nombre": f[1], "tipo": f[2], "raza": f[3], "edad": f[4]},
            "dueno"  : usuarios_map.get(f[5], {"nombre": "Desconocido", "correo": "-"})
        }
        for f in filas
    ]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
