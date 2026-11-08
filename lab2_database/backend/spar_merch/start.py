import asyncio
from database.initialize import initialize


if __name__ == "__main__":
    print("=" * 50)
    print("  Spar Merch API — инициализация БД")
    print("=" * 50)
    asyncio.run(initialize())