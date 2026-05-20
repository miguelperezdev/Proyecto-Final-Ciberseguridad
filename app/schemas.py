from pydantic import BaseModel, field_validator

class ChatRequest(BaseModel):
    task: str
    message: str

    @field_validator("task")
    @classmethod
    def task_must_be_valid(cls, value: str) -> str:
        allowed = {"log_analysis", "alert_classification"}
        if value not in allowed:
            raise ValueError(f"Tarea inválida. Debe ser una de: {allowed}")
        return value

class ChatResponse(BaseModel):
    task: str
    response: str
    timestamp: str