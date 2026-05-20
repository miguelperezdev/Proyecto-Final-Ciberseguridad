from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router
from app.services.audit_service import init_db

app = FastAPI(
    title="CyberDefense Assistant API",
    description="API de ciberseguridad defensiva — Proyecto Final Ciberseguridad",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
app.include_router(chat_router)