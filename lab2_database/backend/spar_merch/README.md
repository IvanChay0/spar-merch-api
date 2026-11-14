#  Spar Merch API — Курсовая работа

Внутренний сервис покупки корпоративного мерча для сотрудников розничной сети **Spar**.

##  Описание

RESTful веб-сервис с полным функционалом:
- Регистрация и JWT-аутентификация сотрудников
- Каталог мерча с CRUD-операциями
- Покупка товаров за бонусные монеты
- P2P-переводы монет между сотрудниками
- Автоматическая генерация отчётов в формате DOCX
- Frontend-приложение (SPA) в фирменных цветах Spar

##  Технологический стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| База данных | PostgreSQL 17 |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (python-jose + bcrypt) |
| Отчёты | python-docx |
| Frontend | Vanilla JS + HTML/CSS (SPA) |
| Сервер | Uvicorn (ASGI) |

##  Запуск

### 1. Установка зависимостей
pip install -r requirements.txt

2. Настройка переменных окружения
Создай файл .env в корне проекта:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/spar_merch
DB_ECHO=False
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_LIFETIME_MINUTES=30
REFRESH_TOKEN_LIFETIME_DAYS=7

3. Инициализация базы данных
python start.py          # создание таблиц + 10 товаров
python database/seed.py  # наполнение тестовыми данными (5 сотрудников, 30 покупок, 15 переводов)

4. Запуск сервера
uvicorn main:app --host 127.0.0.1 --port 8000

. Открыть приложение
Frontend: http://127.0.0.1:8000/
API документация (Swagger): http://127.0.0.1:8000/docs