# Laboratorio: Circuit Breaker — Pet Shop

---

## Requisitos

Solo necesitas **Docker Desktop**: https://www.docker.com/products/docker-desktop/

---

## Estructura

```
laboratorio_circuit_breaker/
├── docker-compose.yml
├── .env                  ← parámetros del Circuit Breaker (no subir al repo)
├── .env.example          ← plantilla de variables de entorno
├── gateway/app.py        ← Circuit Breaker + proxy
├── usuarios/app.py       ← CRUD usuarios
├── backend/app.py        ← CRUD mascotas
└── db/init.sql           ← esquema y datos de prueba
```

---

## Levantar el proyecto

```bash
cp .env.example .env      # solo la primera vez
docker compose up --build
```

---

## Endpoints (gateway en puerto 5000)

| Endpoint    | Descripción                                 |
|-------------|---------------------------------------------|
| `/mascotas` | Lista mascotas — protegido por CB           |
| `/usuarios` | Lista usuarios — protegido por CB           |
| `/resumen`  | Ambos servicios en una sola respuesta       |
| `/relacion` | Mascotas con datos del dueño                |
| `/estado`   | Estado en tiempo real de los circuitos      |

---

## Configuración del Circuit Breaker

Los parámetros se leen desde `.env`. No hay que tocar código.

| Variable           | Default | Descripción                              |
|--------------------|---------|------------------------------------------|
| `CB_UMBRAL_FALLOS` | 2       | Fallos consecutivos que abren el circuito|
| `CB_TIEMPO_ESPERA` | 30      | Segundos en OPEN antes de HALF_OPEN      |
| `CB_TIMEOUT_HTTP`  | 2       | Timeout por petición HTTP (segundos)     |

---

## Estados del circuito

```
CLOSED ──(≥ umbral fallos)──► OPEN
OPEN   ──(tiempo_espera s)──► HALF_OPEN
HALF_OPEN ──(éxito)─────────► CLOSED
HALF_OPEN ──(fallo)─────────► OPEN  (reinicia temporizador)
```

---

## Fases del laboratorio

### Fase 1 — Observar
Levanta el sistema y apaga un servicio:
```bash
docker compose stop backend
```
Haz peticiones a `/mascotas` y revisa el comportamiento en `/estado`.

### Fase 2 — Aplicar
El `gateway/app.py` implementa la clase `CircuitBreaker` con un objeto independiente por servicio:
```python
cb_mascotas = CircuitBreaker("mascotas", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
cb_usuarios = CircuitBreaker("usuarios", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
cb_relacion = CircuitBreaker("relacion", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
```

### Fase 3 — Investigar (Half-Open)
Tras `CB_TIEMPO_ESPERA` segundos en OPEN, el circuito pasa a HALF_OPEN y deja pasar una petición de prueba. Si falla, vuelve a OPEN y reinicia el temporizador.

### Fase 4 — Implementar (Recuperación)
```bash
docker compose start backend   # reinicia el servicio caído
# esperar CB_TIEMPO_ESPERA segundos y hacer una petición → circuito vuelve a CLOSED
```

### Fase 5 — Validar
```bash
docker compose logs -f gateway  # ver transiciones de estado en tiempo real
```
Verificar con `/estado` que los circuitos de cada servicio son independientes.

---

## Notas

- El estado del CircuitBreaker vive en memoria del proceso Flask. En producción con múltiples workers se debería usar Redis.
- El endpoint `/resumen` demuestra la independencia: si mascotas cae, usuarios sigue respondiendo en la misma respuesta.
