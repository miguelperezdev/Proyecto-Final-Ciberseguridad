# Proyecto-Final-Ciberseguridad

# CyberDefense Assistant API

API middleware para el Proyecto Final de Ciberseguridad — Grupo 5.  
El sistema implementa un asistente de IA defensivo para dos tareas controladas: análisis de logs y clasificación de alertas, con validación de entradas, restricciones de rol y registro de interacciones en SQLite .

## Estructura del proyecto

```text
Proyecto-Final-Ciberseguridad/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py
│   └── services/
│       ├── __init__.py
│       ├── audit_service.py
│       ├── ollama_service.py
│       └── validation_service.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── index.js
├── data/
│   └── interactions.db
├── requirements.txt
└── README.md
```

## Descripción general

El asistente fue diseñado para apoyar tareas básicas de ciberdefensa de forma controlada y segura, en línea con el alcance del proyecto académico.  
Las dos tareas implementadas son:

- `log_analysis` — análisis de fragmentos de logs del sistema.
- `alert_classification` — clasificación de alertas de seguridad por nivel de criticidad.

## Requisitos previos

- Python 3.10 o superior.
- Ollama instalado y corriendo en `http://localhost:11434`.
- Modelo descargado localmente:
  ```bash
  ollama pull llama3.2
  ```

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el backend
uvicorn app.main:app --reload
```

El backend quedará disponible en:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Ejecución del frontend

En otra terminal, ubícate en la carpeta `frontend/` y levanta un servidor estático:

```bash
cd frontend
python -m http.server 3000
```

Luego abre en el navegador:

- Chat web: `http://localhost:3000` 

## Flujo de ejecución

Para que el sistema funcione correctamente, deben estar activos estos componentes:

1. Ollama ejecutándose localmente con el modelo `llama3.2`. 
2. Backend FastAPI en el puerto 8000. 
3. Frontend estático en el puerto 3000. 

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check del servicio |
| POST | `/chat` | Envía una solicitud al asistente |
| GET | `/logs` | Devuelve historial de interacciones registradas  |
| GET | `/logs/blocked` | Devuelve únicamente mensajes bloqueados  |

## Ejemplo de uso

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "task": "log_analysis",
    "message": "[2025-05-16 03:14:22] FAILED LOGIN user=root ip=185.220.101.45 attempts=47"
  }'
```

## Ejemplos de tareas soportadas

### 1. Análisis de logs

Entrada:
```text
[2025-05-16 03:14:22] FAILED LOGIN user=root ip=185.220.101.45 attempts=47
[2025-05-16 03:14:23] FAILED LOGIN user=admin ip=185.220.101.45 attempts=12
[2025-05-16 03:14:25] ACCOUNT LOCKED user=root
```

### 2. Clasificación de alertas

Entrada:
```text
Alerta: Se detectó tráfico saliente inusual desde el servidor 192.168.1.15 hacia IP externa 45.33.32.156 en el puerto 443. Volumen transferido: 2.3 GB fuera del horario laboral.
```

## Controles implementados

El proyecto incorpora los controles básicos solicitados en el enunciado :

- Validación de longitud de entrada con máximo de 1500 caracteres. 
- Bloqueo de palabras clave peligrosas como `rm -rf`, `drop table`, `eval(` y `os.system`. 
- Restricción del rol del asistente mediante `SYSTEM_PROMPT`, limitándolo a funciones defensivas. 
- Registro de todas las interacciones en SQLite, incluyendo bloqueos y razones de bloqueo. 

## Base de datos

Las interacciones se almacenan en:

```text
data/interactions.db
```

La tabla `interactions` guarda:

- `timestamp`
- `task`
- `user_msg`
- `ia_resp`
- `blocked`
- `block_reason` 

## Consideraciones y limitaciones

Este proyecto fue diseñado para un entorno académico y controlado, no para producción .  
Actualmente:

- El backend permite CORS abierto con `allow_origins=["*"]`. 
- Los endpoints de auditoría no tienen autenticación. 
- El sistema depende de que Ollama esté disponible localmente. 

## Tecnologías usadas

- FastAPI 
- Uvicorn 
- httpx 
- Pydantic 
- SQLite 
- Ollama + `llama3.2` 

## Tareas soportadas

- `log_analysis` — análisis de logs del sistema. 
- `alert_classification` — clasificación de alertas de seguridad. 

## Autores

- Juan Sebastian Rodriguez Legarda - A00405229
- Miguel Perez Ojeda - A00407054
- Johan Stiven Suarez Perdomo - A00404253

