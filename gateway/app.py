import os
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)



class CircuitBreaker:

    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, nombre: str, umbral_fallos: int, tiempo_espera: int):
        self.nombre        = nombre
        self.umbral_fallos = umbral_fallos
        self.tiempo_espera = tiempo_espera
        self.estado          = self.CLOSED
        self.fallos          = 0
        self.tiempo_apertura = None

    def llamar(self, url: str, timeout: int = 2):
        """Ejecuta GET a url respetando el estado del circuito."""

        if self.estado == self.OPEN:
            transcurridos = time.time() - self.tiempo_apertura
            restantes     = round(self.tiempo_espera - transcurridos, 1)

            if transcurridos >= self.tiempo_espera:
                print(f"[CB:{self.nombre}] {self.tiempo_espera}s cumplidos → HALF_OPEN", flush=True)
                self.estado = self.HALF_OPEN
            else:
                print(f"[CB:{self.nombre}] OPEN — reintento en {restantes}s", flush=True)
                return {
                    "error"             : f"Servicio '{self.nombre}' bloqueado temporalmente.",
                    "estado_circuito"   : self.estado,
                    "reintentar_en_seg" : restantes
                }, 503

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            self._en_exito()
            return response.json(), 200
        except Exception as exc:
            return self._en_fallo(str(exc))

    def _en_exito(self):
        if self.estado == self.HALF_OPEN:
            print(f"[CB:{self.nombre}] HALF_OPEN exitoso → CLOSED", flush=True)
        self.estado          = self.CLOSED
        self.fallos          = 0
        self.tiempo_apertura = None

    def _en_fallo(self, motivo: str):
        self.fallos += 1
        print(f"[CB:{self.nombre}] Fallo #{self.fallos} — {motivo}", flush=True)

        if self.estado == self.HALF_OPEN:
            print(f"[CB:{self.nombre}] Fallo en HALF_OPEN → OPEN (temporizador reiniciado)", flush=True)
            self.estado          = self.OPEN
            self.tiempo_apertura = time.time()

        elif self.fallos >= self.umbral_fallos:
            print(f"[CB:{self.nombre}] Umbral alcanzado → OPEN por {self.tiempo_espera}s", flush=True)
            self.estado          = self.OPEN
            self.tiempo_apertura = time.time()

        return {
            "error"             : f"Servicio '{self.nombre}' no disponible.",
            "estado_circuito"   : self.estado,
            "fallos_acumulados" : self.fallos
        }, 503

    def info(self) -> dict:
        data = {"servicio": self.nombre, "estado": self.estado, "fallos": self.fallos}
        if self.estado == self.OPEN and self.tiempo_apertura:
            restante = round(self.tiempo_espera - (time.time() - self.tiempo_apertura), 1)
            data["reintentar_en_seg"] = max(restante, 0)
        return data




CB_UMBRAL_FALLOS = int(os.getenv("CB_UMBRAL_FALLOS", 2))
CB_TIEMPO_ESPERA = int(os.getenv("CB_TIEMPO_ESPERA", 30))
CB_TIMEOUT_HTTP  = int(os.getenv("CB_TIMEOUT_HTTP",  2))

URL_BACKEND  = os.getenv("URL_BACKEND",  "http://backend:5000")
URL_USUARIOS = os.getenv("URL_USUARIOS", "http://usuarios:5000")

# Un CircuitBreaker independiente por servicio
cb_mascotas = CircuitBreaker("mascotas", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
cb_usuarios = CircuitBreaker("usuarios", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
cb_relacion = CircuitBreaker("relacion", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)


#  ENDPOINTS

@app.route("/")
def home():
    return "Gateway funcionando"

@app.route("/mascotas")
def mascotas():
    datos, codigo = cb_mascotas.llamar(f"{URL_BACKEND}/mascotas", CB_TIMEOUT_HTTP)
    return jsonify(datos), codigo


@app.route("/usuarios")
def usuarios():
    datos, codigo = cb_usuarios.llamar(f"{URL_USUARIOS}/usuarios", CB_TIMEOUT_HTTP)
    return jsonify(datos), codigo


@app.route("/resumen")
def resumen():
    """Consulta ambos servicios; demuestra que los circuitos son independientes."""
    datos_mascotas, cod_m = cb_mascotas.llamar(f"{URL_BACKEND}/mascotas",  CB_TIMEOUT_HTTP)
    datos_usuarios, cod_u = cb_usuarios.llamar(f"{URL_USUARIOS}/usuarios", CB_TIMEOUT_HTTP)

    return jsonify({
        "mascotas": datos_mascotas if cod_m == 200 else {"error": datos_mascotas},
        "usuarios": datos_usuarios if cod_u == 200 else {"error": datos_usuarios},
    }), 200





@app.route("/estado")
def estado_circuitos():
    """Estado actual de todos los circuitos."""
    return jsonify({"circuitos": [cb_mascotas.info(), cb_usuarios.info(), cb_relacion.info()]})

@app.route("/relacion")
def relacion():
    """
    Endpoint central en el gateway.

    - Si mascotas y usuarios funcionan: muestra la relación completa.
    - Si usuarios falla: muestra solo mascotas.
    - Si mascotas falla: muestra solo usuarios.
    - Si ambos fallan: muestra mensaje de error.
    """

    URL_BACKEND = os.getenv("URL_BACKEND", "http://backend:5000").rstrip("/")
    URL_USUARIOS = os.getenv("URL_USUARIOS", "http://usuarios:5000").rstrip("/")

    mascotas = []
    usuarios = []

    servicio_mascotas = "activo"
    servicio_usuarios = "activo"

    # 1. Intentar consultar mascotas
    try:
        respuesta_mascotas = requests.get(f"{URL_BACKEND}/mascotas", timeout=2)
        respuesta_mascotas.raise_for_status()

        data_mascotas = respuesta_mascotas.json()

        if isinstance(data_mascotas, list):
            mascotas = data_mascotas
        else:
            mascotas = data_mascotas.get("mascotas", [])

    except Exception as e:
        print(f"[gateway] No está funcionando mascotas: {e}", flush=True)
        servicio_mascotas = "apagado"

    # 2. Intentar consultar usuarios
    try:
        respuesta_usuarios = requests.get(f"{URL_USUARIOS}/usuarios", timeout=2)
        respuesta_usuarios.raise_for_status()

        data_usuarios = respuesta_usuarios.json()

        if isinstance(data_usuarios, list):
            usuarios = data_usuarios
        else:
            usuarios = data_usuarios.get("usuarios", [])

    except Exception as e:
        print(f"[gateway] No está funcionando usuarios: {e}", flush=True)
        servicio_usuarios = "apagado"

    # 3. Si ambos servicios funcionan
    if servicio_mascotas == "activo" and servicio_usuarios == "activo":
        usuarios_map = {u["id"]: u for u in usuarios}

        relaciones = []

        for mascota in mascotas:
            relaciones.append({
                "mascota": mascota,
                "usuario": usuarios_map.get(
                    mascota.get("id_usuario"),
                    {"mensaje": "Dueño no encontrado"}
                )
            })

        return jsonify({
            "mensaje": "Mascotas y usuarios funcionando correctamente.",
            "servicio_mascotas": servicio_mascotas,
            "servicio_usuarios": servicio_usuarios,
            "relaciones": relaciones
        })

    # 4. Si usuarios está apagado, pero mascotas funciona
    if servicio_mascotas == "activo" and servicio_usuarios == "apagado":
        return jsonify({
            "mensaje": "No está funcionando usuarios. Se muestran solamente las mascotas.",
            "servicio_mascotas": servicio_mascotas,
            "servicio_usuarios": servicio_usuarios,
            "mascotas": mascotas
        })

    # 5. Si mascotas está apagado, pero usuarios funciona
    if servicio_mascotas == "apagado" and servicio_usuarios == "activo":
        return jsonify({
            "mensaje": "No está funcionando mascotas. Se muestran solamente los usuarios.",
            "servicio_mascotas": servicio_mascotas,
            "servicio_usuarios": servicio_usuarios,
            "usuarios": usuarios
        })

    # 6. Si ambos están apagados
    return jsonify({
        "mensaje": "No está funcionando mascotas ni usuarios.",
        "servicio_mascotas": servicio_mascotas,
        "servicio_usuarios": servicio_usuarios
    }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
