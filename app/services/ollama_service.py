import httpx
from fastapi import HTTPException
from app.config import OLLAMA_URL, OLLAMA_MODEL, SYSTEM_PROMPT

async def query_ollama(full_user_msg: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_user_msg},
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

    return data.get("message", {}).get("content", "Sin respuesta del modelo.")