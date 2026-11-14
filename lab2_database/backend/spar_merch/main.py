from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from api import api_router

app = FastAPI(
    title="Spar Merch API",
    description="Внутренний сервис покупки корпоративного мерча для сотрудников Spar",
    version="1.0.0",
)

# CORS (для фронтенда, если он будет на другом порту)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роутеры
app.include_router(api_router, prefix="/api/v1")

# Статика фронтенда
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_frontend():
    """Главная страница — отдаём SPA."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}