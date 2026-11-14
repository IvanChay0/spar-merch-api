from fastapi import FastAPI
from api.endpoints import merch  # Импортируем напрямую

app = FastAPI(
    title="Spar Merch API",
    description="Внутренний сервис покупки корпоративного мерча для сотрудников Spar",
    version="1.0.0",
)

# Подключаем роутер напрямую
app.include_router(merch.router, prefix="/api/v1/merch", tags=["merch"])


@app.get("/")
async def root():
    return {"message": "Spar Merch API is running. Перейдите в /docs для документации."}