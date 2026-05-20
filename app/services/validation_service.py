from app.config import MAX_INPUT, BLOCKED_KEYWORDS

def validate_input(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "El mensaje no puede estar vacío."
    if len(text) > MAX_INPUT:
        return False, f"El mensaje excede el límite de {MAX_INPUT} caracteres."

    text_lower = text.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in text_lower:
            return False, f"Contenido bloqueado: el mensaje contiene '{kw}'."

    return True, ""