from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import httpx
import sqlite3
import datetime
import re
import os

# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"          # cambia a gemma3:4b si tienes más RAM
MAX_INPUT    = 1500                # caracteres máximos por mensaje
DB_FILE      = "interactions.db"

# Palabras bloqueadas (control de seguridad)
BLOCKED_KEYWORDS = [
    "rm -rf", "drop table", "delete from", "format c:",
    "shutdown", "exec(", "eval(", "os.system", "subprocess"
]

# System prompt que define el rol del asistente
SYSTEM_PROMPT = """
Eres CyberDefense Assistant, un asistente de ciberseguridad defensiva.
Tu función es ÚNICAMENTE apoyar al analista humano en las siguientes tareas:
1. Análisis de logs del sistema — identificar eventos sospechosos o anómalos.
2. Clasificación de alertas de seguridad — categorizar por nivel: CRÍTICO, ALTO, MEDIO, BAJO.

REGLAS ESTRICTAS:
- Solo respondes sobre análisis defensivo de seguridad informática.
- Nunca sugieres cómo atacar sistemas, obtener acceso no autorizado, ni ejecutar comandos destructivos.
- Si el usuario pide algo fuera de tu rol, responde: "Esa solicitud está fuera de mi alcance como asistente defensivo."
- Siempre aclara que tus sugerencias son orientativas y la decisión final la toma el analista humano.
- Responde en español, de forma clara y estructurada.
"""

# ──────────────────────────────────────────────
#  BASE DE DATOS (registro de interacciones)
# ──────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            task      TEXT    NOT NULL,
            user_msg  TEXT    NOT NULL,
            ia_resp   TEXT,
            blocked   INTEGER DEFAULT 0,
            block_reason TEXT
        )
    """)
    con.commit()
    con.close()

def log_interaction(task: str, user_msg: str, ia_resp: str = None,
                    blocked: bool = False, block_reason: str = None):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "INSERT INTO interactions(timestamp,task,user_msg,ia_resp,blocked,block_reason) VALUES(?,?,?,?,?,?)",
        (datetime.datetime.now().isoformat(), task, user_msg,
         ia_resp, int(blocked), block_reason)
    )
    con.commit()
    con.close()

# ──────────────────────────────────────────────
#  VALIDACIONES (reglas simples)
# ──────────────────────────────────────────────
def validate_input(text: str) -> tuple[bool, str]:
    """Retorna (es_valido, motivo_si_invalido)"""
    if not text or not text.strip():
        return False, "El mensaje no puede estar vacío."
    if len(text) > MAX_INPUT:
        return False, f"El mensaje excede el límite de {MAX_INPUT} caracteres."
    text_lower = text.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in text_lower:
            return False, f"Contenido bloqueado: el mensaje contiene '{kw}'."
    return True, ""

# ──────────────────────────────────────────────
#  APP FASTAPI
# ──────────────────────────────────────────────
app = FastAPI(
    title="CyberDefense Assistant API",
    description="API de ciberseguridad defensiva — Proyecto Final Ciberseguridad",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en producción real, restringir al dominio del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# ──────────────────────────────────────────────
#  MODELOS DE DATOS
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    task: str       # "log_analysis" | "alert_classification"
    message: str

    @validator("task")
    def task_must_be_valid(cls, v):
        allowed = {"log_analysis", "alert_classification"}
        if v not in allowed:
            raise ValueError(f"Tarea inválida. Debe ser una de: {allowed}")
        return v

class ChatResponse(BaseModel):
    task: str
    response: str
    timestamp: str

# ──────────────────────────────────────────────
#  PROMPTS POR TAREA
# ──────────────────────────────────────────────
TASK_PROMPTS = {
    "log_analysis": (
        "El analista te entrega el siguiente fragmento de log del sistema. "
        "Identifica cada evento sospechoso o anómalo, explica por qué es sospechoso "
        "y sugiere qué acción debería tomar el analista. "
        "Organiza tu respuesta en formato: [EVENTO] → [NIVEL DE RIESGO] → [RECOMENDACIÓN].\n\n"
        "LOG:\n"
    ),
    "alert_classification": (
        "El analista reporta la siguiente alerta de seguridad. "
        "Clasifícala con nivel: CRÍTICO / ALTO / MEDIO / BAJO. "
        "Explica brevemente el criterio de clasificación y sugiere los próximos pasos defensivos. "
        "Formato: [CLASIFICACIÓN] → [JUSTIFICACIÓN] → [PRÓXIMOS PASOS].\n\n"
        "ALERTA:\n"
    ),
}

# ──────────────────────────────────────────────
#  ENDPOINTS
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "CyberDefense Assistant API v1.0.0"}


@app.post("/chat", response_model=ChatResponse, tags=["Assistant"])
async def chat(req: ChatRequest):
    # 1. Validar entrada
    valid, reason = validate_input(req.message)
    if not valid:
        log_interaction(req.task, req.message, blocked=True, block_reason=reason)
        raise HTTPException(status_code=400, detail=reason)

    # 2. Construir prompt enriquecido con contexto de tarea
    task_context = TASK_PROMPTS.get(req.task, "")
    full_user_msg = task_context + req.message

    # 3. Llamar a Ollama
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": full_user_msg},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar a Ollama. Asegúrate de que está corriendo en localhost:11434"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar el modelo: {str(e)}")

    # 4. Extraer respuesta
    ia_response = data.get("message", {}).get("content", "Sin respuesta del modelo.")
    timestamp   = datetime.datetime.now().isoformat()

    # 5. Registrar interacción
    log_interaction(req.task, req.message, ia_resp=ia_response)

    return ChatResponse(task=req.task, response=ia_response, timestamp=timestamp)


@app.get("/logs", tags=["Audit"])
def get_logs(limit: int = 50):
    """Devuelve las últimas interacciones registradas (para auditoría)."""
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT id,timestamp,task,user_msg,ia_resp,blocked,block_reason "
        "FROM interactions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    con.close()
    return [
        {
            "id": r[0], "timestamp": r[1], "task": r[2],
            "user_msg": r[3], "ia_resp": r[4],
            "blocked": bool(r[5]), "block_reason": r[6]
        }
        for r in rows
    ]


@app.get("/logs/blocked", tags=["Audit"])
def get_blocked_logs():
    """Devuelve solo las interacciones que fueron bloqueadas."""
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT id,timestamp,task,user_msg,block_reason "
        "FROM interactions WHERE blocked=1 ORDER BY id DESC"
    ).fetchall()
    con.close()
    return [
        {"id": r[0], "timestamp": r[1], "task": r[2],
         "user_msg": r[3], "block_reason": r[4]}
        for r in rows
    ]
