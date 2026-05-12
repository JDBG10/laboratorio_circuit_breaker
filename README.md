Listo, Juan. Organicé tu README completo con las correcciones: estructura correcta, ruta `/corte_3/laboratorio_circuit_breaker/`, sin subir `.env`, Fase 1 mejor explicada y tabla de comandos al final. Tomé como base el README que subiste. 

Copia y pega esto completo en tu `README.md`:

````markdown
# Laboratorio: Sistema que aprende a fallar

Implementación del patrón **Circuit Breaker** usando microservicios con **Flask** y **Docker Compose**.

El objetivo del laboratorio es analizar el comportamiento de un sistema distribuido cuando uno de sus servicios falla, y aplicar una solución que permita proteger el gateway, controlar los errores y recuperar el servicio de forma automática.

---

## Integrante

- Juan David Bolaños Galindo

---

## Descripción general

Este laboratorio implementa el patrón **Circuit Breaker** en un sistema tipo **Pet Shop**, compuesto por varios servicios.

El sistema cuenta con un **gateway en Flask**, encargado de recibir las peticiones del usuario y redirigirlas a los servicios correspondientes.

Los servicios principales son:

- Mascotas
- Usuarios
- Relación mascota-usuario
- Resumen

El Circuit Breaker permite controlar los fallos de los servicios.  
Cuando un servicio deja de responder, el gateway no sigue insistiendo de forma indefinida. En cambio, abre el circuito, bloquea temporalmente las peticiones y luego realiza una prueba para verificar si el servicio ya se recuperó.

---

## Tecnologías utilizadas

- Python
- Flask
- Docker
- Docker Compose
- Requests
- Variables de entorno `.env`

---

## Requisitos

Para ejecutar el proyecto se necesita:

- Docker Desktop instalado y en ejecución.

---

## Ruta de entrega solicitada

La entrega del laboratorio debe quedar organizada de la siguiente manera:

```bash
/corte_3/
└── laboratorio_circuit_breaker/
    ├── README.md
    ├── docker-compose.yml
    ├── .env.example
    ├── .gitignore
    ├── gateway/
    ├── usuarios/
    ├── backend/
    ├── db/
    └── evidencias/
```

---

## Estructura del repositorio

```bash
laboratorio_circuit_breaker/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── gateway/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── usuarios/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   └── init.sql
└── evidencias/
    ├── fase1.png
    ├── fase2.png
    ├── fase3.png
    ├── fase4.png
    ├── fase5.png
    └── half-open-circuit-breaker.png
```

> El archivo `.env` se crea localmente a partir de `.env.example`, pero no se sube al repositorio porque contiene la configuración del proyecto.

---

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

---

### 2. Entrar a la carpeta del proyecto

```bash
cd corte_3/laboratorio_circuit_breaker
```

---

### 3. Crear el archivo `.env`

```bash
cp .env.example .env
```

---

### 4. Levantar los servicios

```bash
docker compose up --build
```

---

### 5. Verificar contenedores activos

```bash
docker compose ps
```

---

### 6. Ver logs del gateway

```bash
docker compose logs -f gateway
```

---

## Endpoints disponibles

| Endpoint | URL | Descripción |
|---|---|---|
| `/mascotas` | `http://localhost:5000/mascotas` | Lista las mascotas |
| `/usuarios` | `http://localhost:5000/usuarios` | Lista los usuarios |
| `/resumen` | `http://localhost:5000/resumen` | Muestra información combinada |
| `/relacion` | `http://localhost:5000/relacion` | Relaciona mascotas con usuarios |
| `/estado` | `http://localhost:5000/estado` | Muestra el estado de los circuitos |

---

## Configuración del Circuit Breaker

Los parámetros del sistema se configuran desde el archivo `.env`.

```env
# Número de fallos consecutivos para abrir el circuito
CB_UMBRAL_FALLOS=3

# Tiempo de espera antes de intentar recuperación
CB_TIEMPO_ESPERA=15

# Timeout HTTP por petición
CB_TIMEOUT_HTTP=2
```

---

## Funcionamiento del Circuit Breaker

El sistema implementa tres estados principales:

| Estado | Descripción |
|---|---|
| `CLOSED` | El servicio funciona normalmente y las peticiones pasan |
| `OPEN` | El circuito se abre porque el servicio falló varias veces |
| `HALF_OPEN` | Se permite una petición de prueba para saber si el servicio ya se recuperó |

---

## Flujo del circuito

```txt
CLOSED ──(fallos consecutivos)──► OPEN
OPEN ──(tiempo de espera)───────► HALF_OPEN
HALF_OPEN ──(éxito)─────────────► CLOSED
HALF_OPEN ──(fallo)─────────────► OPEN
```

---

# FASE 1 – OBSERVAR

## Objetivo

Analizar el comportamiento del sistema cuando se apaga un servicio y observar cómo responde el gateway ante los fallos.

---

## Procedimiento

Se apagó el servicio de mascotas:

```bash
docker compose stop backend
```

Luego se realizaron peticiones al endpoint:

```txt
http://localhost:5000/mascotas
```

También se revisaron los logs del gateway:

```bash
docker compose logs -f gateway
```

---

## Resultado observado

En esta fase se observó el comportamiento inicial del sistema al apagar el servicio de mascotas.

Como el endpoint `/mascotas` ya tenía una lógica básica de Circuit Breaker trabajada en clase, el gateway detectó los fallos y abrió el circuito después de varios intentos.

Esto permitió que el sistema no siguiera insistiendo todo el tiempo sobre el servicio caído.

---

## Respuestas de la fase

| Pregunta | Respuesta |
|---|---|
| ¿Qué hace el sistema actualmente? | El gateway intenta comunicarse con el servicio de mascotas. Al detectar varios fallos, abre el circuito. |
| ¿Se protege o insiste? | El sistema se protege, porque después de varios fallos deja de enviar peticiones al servicio caído por un tiempo definido. |

---

## Evidencia

![Fase 1](evidencias/fase1.png)

---

# FASE 2 – APLICAR

## Objetivo

Extender el patrón Circuit Breaker a varios servicios del sistema, no solo al endpoint de mascotas.

---

## Qué se hizo

Se aplicó el Circuit Breaker a varios endpoints del gateway:

```txt
/mascotas
/usuarios
/relacion
/resumen
```

Se creó un circuito independiente por servicio:

```python
cb_mascotas = CircuitBreaker("mascotas", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)

cb_usuarios = CircuitBreaker("usuarios", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)

cb_relacion = CircuitBreaker("relacion", CB_UMBRAL_FALLOS, CB_TIEMPO_ESPERA)
```

---

## Decisiones tomadas

| Pregunta | Respuesta |
|---|---|
| ¿Cada servicio debe tener su propio contador de fallos? | Sí. Cada servicio debe tener su propio contador porque no todos fallan al mismo tiempo. |
| ¿El circuito debe abrirse de forma independiente por servicio? | Sí. Si falla mascotas, solo se abre el circuito de mascotas, pero usuarios puede seguir funcionando. |
| ¿Qué pasa si falla un servicio pero el otro sigue funcionando? | El servicio que falla queda bloqueado temporalmente, pero los demás servicios siguen respondiendo normalmente. |

---

## Explicación breve

Se decidió manejar un Circuit Breaker independiente por servicio.  
Esto permite que el sistema sea más estable, porque la falla de un servicio no afecta de forma directa a los demás.

También se configuraron los parámetros desde el archivo `.env`, para evitar dejar valores fijos dentro del código.

---

## Evidencia

![Fase 2](evidencias/fase2.png)

---

# FASE 3 – INVESTIGAR

## Objetivo

Comprender el funcionamiento del estado `HALF_OPEN` dentro del patrón Circuit Breaker.

---

## ¿Qué significa HALF_OPEN?

`HALF_OPEN` significa que el sistema entra en un estado de prueba.

Cuando el circuito está en `OPEN`, el gateway bloquea temporalmente las peticiones hacia el servicio que falló.

Después de cumplirse el tiempo de espera configurado, el circuito pasa a `HALF_OPEN`.  
En ese momento, el gateway permite una sola petición de prueba para saber si el servicio ya volvió a funcionar.

---

## ¿Cuándo se vuelve a intentar una llamada?

Se vuelve a intentar una llamada cuando ya pasó el tiempo de espera definido en la configuración.

En este laboratorio, el tiempo de espera usado fue:

```env
CB_TIEMPO_ESPERA=15
```

Esto significa que el gateway espera 15 segundos antes de probar nuevamente el servicio.

---

## ¿Qué pasa si el servicio vuelve a fallar?

Si la petición de prueba falla, el circuito vuelve al estado `OPEN`.

```txt
HALF_OPEN → OPEN
```

Esto quiere decir que el servicio todavía no está listo y el gateway lo vuelve a bloquear temporalmente.

---

## ¿Qué pasa si la prueba funciona?

Si la petición de prueba funciona correctamente, el circuito vuelve al estado `CLOSED`.

```txt
HALF_OPEN → CLOSED
```

Esto significa que el servicio ya se recuperó y puede recibir peticiones normalmente.

---

## Imagen explicativa de HALF_OPEN

<p align="center">
  <img src="evidencias/half-open-circuit-breaker.png" alt="Explicación del estado HALF_OPEN en Circuit Breaker" width="850">
</p>

---

## Evidencia

![Fase 3](evidencias/fase3.png)

---

# FASE 4 – IMPLEMENTAR

## Objetivo

Implementar la recuperación automática del circuito después de un tiempo de espera.

---

## Qué se hizo

Se implementó la lógica para que el circuito pase automáticamente de `OPEN` a `HALF_OPEN` cuando se cumple el tiempo configurado.

Código principal:

```python
if self.estado == self.OPEN:
    if time.time() - self.tiempo_apertura >= self.tiempo_espera:
        self.estado = self.HALF_OPEN
```

---

## Explicación del código

El código revisa si el circuito está abierto.  
Si está en estado `OPEN`, compara el tiempo actual con el momento en que se abrió el circuito.

Cuando ya pasó el tiempo de espera, el circuito cambia a `HALF_OPEN` y permite hacer una prueba para saber si el servicio se recuperó.

---

## Procedimiento de prueba

Primero se apagó el servicio de mascotas:

```bash
docker compose stop backend
```

Luego se hicieron peticiones a:

```txt
http://localhost:5000/mascotas
```

Después se volvió a iniciar el servicio:

```bash
docker compose start backend
```

Cuando pasó el tiempo definido, el circuito pasó a `HALF_OPEN`.

Si la petición de prueba funcionaba, el circuito volvía a `CLOSED`.

---

## Parámetros usados

| Variable | Valor |
|---|---|
| `CB_UMBRAL_FALLOS` | 3 |
| `CB_TIEMPO_ESPERA` | 15 segundos |
| `CB_TIMEOUT_HTTP` | 2 segundos |

---

## Flujo validado

Cuando el servicio se recupera:

```txt
CLOSED → OPEN → HALF_OPEN → CLOSED
```

Cuando el servicio sigue fallando:

```txt
HALF_OPEN → OPEN
```

---

## Evidencia

![Fase 4](evidencias/fase4.png)

---

# FASE 5 – VALIDAR

## Objetivo

Comprobar el funcionamiento completo del Circuit Breaker en diferentes escenarios.

---

## Escenario 1: Servicio funcionando

Con todos los servicios activos:

```bash
docker compose up --build
```

Se consulta el endpoint:

```txt
http://localhost:5000/estado
```

Resultado esperado:

```json
{
  "servicio": "mascotas",
  "estado": "CLOSED",
  "fallos": 0
}
```

---

## Escenario 2: Servicio caído

Se apaga el backend:

```bash
docker compose stop backend
```

Se prueba el endpoint:

```txt
http://localhost:5000/mascotas
```

Resultado esperado:

```json
{
  "error": "Servicio 'mascotas' no disponible.",
  "estado_circuito": "OPEN",
  "fallos_acumulados": 3
}
```

---

## Escenario 3: Circuito abierto

Cuando el circuito está en estado `OPEN`, el sistema no sigue insistiendo al servicio caído.

Resultado esperado:

```json
{
  "error": "Servicio 'mascotas' bloqueado temporalmente.",
  "estado_circuito": "OPEN",
  "reintentar_en_seg": 15
}
```

---

## Escenario 4: Recuperación automática

Se vuelve a iniciar el backend:

```bash
docker compose start backend
```

Después de esperar el tiempo configurado, se realiza una nueva petición.

Si el servicio responde correctamente, el circuito vuelve a estado `CLOSED`.

---

## Escenario 5: Servicios independientes

Si falla el servicio de mascotas, el servicio de usuarios puede seguir funcionando.

Ejemplo en `/estado`:

```json
{
  "circuitos": [
    {
      "servicio": "mascotas",
      "estado": "OPEN",
      "fallos": 3
    },
    {
      "servicio": "usuarios",
      "estado": "CLOSED",
      "fallos": 0
    }
  ]
}
```

---

## Resultado general de validación

| Escenario probado | Resultado |
|---|---|
| Servicio funcionando | El gateway respondió correctamente. |
| Servicio caído | El gateway detectó los fallos. |
| Circuito abierto | El gateway bloqueó temporalmente las peticiones. |
| Recuperación del servicio | El circuito pasó a `HALF_OPEN` y luego a `CLOSED`. |
| Servicios independientes | La falla de un servicio no afectó a los demás. |

---

## Evidencia

![Fase 5](evidencias/fase5.png)

---

# Código implementado

El código principal se encuentra en:

```bash
gateway/app.py
```

Se implementó:

- Clase `CircuitBreaker`
- Estados `CLOSED`, `OPEN` y `HALF_OPEN`
- Contador de fallos por servicio
- Circuito independiente para mascotas
- Circuito independiente para usuarios
- Circuito independiente para relación
- Endpoint `/estado`
- Recuperación automática con `HALF_OPEN`
- Parámetros configurables desde `.env`

---

# Logs esperados

Durante las pruebas, en los logs del gateway se pueden observar mensajes similares a los siguientes:

```bash
[CB:mascotas] Fallo #1
[CB:mascotas] Fallo #2
[CB:mascotas] Fallo #3
[CB:mascotas] Umbral alcanzado → OPEN
[CB:mascotas] OPEN — reintento en 15s
[CB:mascotas] Tiempo cumplido → HALF_OPEN
[CB:mascotas] HALF_OPEN exitoso → CLOSED
```

Estos logs ayudan a confirmar que el Circuit Breaker está cambiando correctamente de estado.

---

# Tabla de comandos utilizados

| Comando | ¿Para qué se usa? |
|---|---|
| `docker compose up --build` | Levanta y construye todos los servicios del proyecto. |
| `docker compose ps` | Muestra qué contenedores están activos. |
| `docker compose logs -f gateway` | Muestra los logs del gateway en tiempo real. |
| `docker compose logs -f backend` | Muestra los logs del servicio de mascotas. |
| `docker compose logs -f usuarios` | Muestra los logs del servicio de usuarios. |
| `docker compose stop backend` | Apaga el servicio de mascotas para probar fallos. |
| `docker compose start backend` | Vuelve a encender el servicio de mascotas. |
| `docker compose stop usuarios` | Apaga el servicio de usuarios para probar fallos. |
| `docker compose start usuarios` | Vuelve a encender el servicio de usuarios. |
| `git add README.md evidencias/` | Agrega el README y las imágenes al repositorio. |
| `git commit -m "Agrega evidencias del laboratorio Circuit Breaker"` | Guarda los cambios realizados. |
| `git push` | Sube los cambios al repositorio remoto. |

---

# Análisis final

## ¿Qué cambió en el comportamiento del sistema?

Antes, el gateway podía seguir intentando conectarse a un servicio caído.

Ahora, con el Circuit Breaker, el sistema detecta los fallos, abre el circuito, espera un tiempo y luego prueba si el servicio se recuperó.

Esto permite que el sistema falle de forma controlada y no afecte todos los servicios.

---

## ¿Qué decisiones se tomaron en la implementación?

Se decidió usar un Circuit Breaker independiente por servicio.

Esto permite que cada servicio tenga su propio contador de fallos y su propio estado.

También se agregó el estado `HALF_OPEN`, porque permite validar si un servicio se recuperó sin necesidad de reiniciar el gateway.

Además, se decidió manejar la configuración desde el archivo `.env.example`, para que los valores como el número de fallos, el tiempo de espera y el timeout puedan modificarse fácilmente.

---

## ¿Qué dificultades se encontraron?

Durante la práctica se encontraron algunas dificultades:

- Entender que cada servicio debía manejar sus fallos de forma independiente.
- Validar correctamente los cambios de estado.
- Revisar los logs para confirmar el paso de `CLOSED` a `OPEN`, luego a `HALF_OPEN` y finalmente a `CLOSED`.
- Ajustar los tiempos de espera para observar mejor el comportamiento del circuito.
- Probar varias veces apagando y encendiendo servicios para comprobar la recuperación.

---

# Mejoras obtenidas

Con la implementación del Circuit Breaker se obtuvieron las siguientes mejoras:

| Mejora | Explicación |
|---|---|
| Recuperación automática | El sistema puede volver a probar si el servicio ya funciona. |
| Independencia entre servicios | Si falla un servicio, los demás pueden seguir funcionando. |
| Configuración externa | Los valores principales se manejan desde `.env.example`. |
| Respuestas más rápidas | El gateway no pierde tiempo insistiendo sobre servicios caídos. |
| Monitoreo | El endpoint `/estado` permite ver cómo están los circuitos. |
| Mayor estabilidad | El sistema responde de forma más controlada ante fallos. |

---

# Conclusión

La implementación del patrón Circuit Breaker permitió mejorar la resiliencia del sistema distribuido.

El gateway ahora puede detectar cuando un servicio no responde, abrir el circuito, evitar llamadas innecesarias y permitir una recuperación automática mediante el estado `HALF_OPEN`.

Además, al manejar circuitos independientes por servicio, el sistema puede seguir funcionando parcialmente aunque uno de los servicios falle.

Con esta implementación, el sistema Pet Shop es más tolerante a fallos, más estable y más adecuado para una arquitectura basada en microservicios.

---

## Autor

**Juan David Bolaños Galindo**  
Estudiante de Ingeniería de Sistemas  

Proyecto académico desarrollado para el laboratorio de resiliencia y tolerancia a fallos con microservicios, aplicando conceptos de microservicios, Docker, API Gateway y Circuit Breaker.
````
