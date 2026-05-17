# Proyecto-Final-Ciberseguridad

# CyberDefense Assistant API

API middleware para el Proyecto Final de Ciberseguridad — Grupo 5.

## Requisitos previos
- Python 3.10+
- Ollama instalado y corriendo en `http://localhost:11434`
- Modelo descargado: `ollama pull llama3.2`

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

# 3. Ejecutar el servidor
uvicorn main:app --reload
```

El servidor queda disponible en: http://localhost:8000

Documentación interactiva (Swagger): http://localhost:8000/docs

## Visualización
Primero, ejecutar este comando en una terminal:

```bash
python -m http.server 3000
```

Luego, acceder al chat con la URL:  http://localhost:3000




## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/chat` | Enviar mensaje al asistente |
| GET | `/logs` | Ver historial de interacciones |
| GET | `/logs/blocked` | Ver mensajes bloqueados |

## Ejemplo de uso

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "task": "log_analysis",
    "message": "[2025-05-16 03:14:22] FAILED LOGIN user=root ip=185.220.101.45 attempts=47"
  }'
```

## Tareas soportadas
- `log_analysis` — Análisis de logs del sistema
- `alert_classification` — Clasificación de alertas de seguridad

## Controles implementados
- Validación de longitud de entrada (máx. 1500 caracteres)
- Bloqueo de palabras clave peligrosas
- Restricción de rol via system prompt
- Registro de todas las interacciones en SQLite (`interactions.db`)


