from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from core.config import Settings, get_settings
from database.base import Base
# ВАЖНО: импорт всех моделей, чтобы SQLAlchemy "увидел" их
# Импортируем все модели, чтобы SQLAlchemy увидел их при создании таблиц
from database.tables.entities.employee import Employee  # noqa: F401
from database.tables.entities.merch_item import MerchItem  # noqa: F401
from database.tables.junctions.purchase import Purchase  # noqa: F401
from database.tables.junctions.transfer import Transfer  # noqa: F401
from database.tables.entities import MerchItem as MerchItemEntity


# Начальные товары мерча Spar
INITIAL_PRODUCTS = [
    {"name": "Худи Spar", "price": 300},
    {"name": "Футболка Spar", "price": 80},
    {"name": "Кружка Spar", "price": 20},
    {"name": "Ручка с логотипом", "price": 10},
    {"name": "Пауэрбанк Spar", "price": 200},
    {"name": "Зонт Spar", "price": 200},
    {"name": "Носки Spar", "price": 10},
    {"name": "Кошелёк Spar", "price": 50},
    {"name": "Книга о компании", "price": 50},
    {"name": "Розовое худи (редкое)", "price": 500},
]


async def initialize():
    """
    Инициализация базы данных:
    1. Удаляет все существующие таблицы (ОСТОРОЖНО!)
    2. Создаёт таблицы заново по описанным моделям
    3. Заполняет таблицу merch_item начальными товарами
    """
    settings: Settings = get_settings()

    engine: AsyncEngine = create_async_engine(
        url=settings.DATABASE_URL,
        echo=settings.DB_ECHO,
    )

    try:
        # 1. Удаляем старые таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("\033[93m[INFO] Старые таблицы удалены.\033[0m")

        # 2. Создаём новые таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("\033[92m[INFO] Таблицы успешно созданы.\033[0m")

        # 3. Заполняем товары, если их ещё нет
        async with AsyncSession(engine) as session:
            existing = await session.execute(select(MerchItemEntity.name))
            existing_names = {row[0] for row in existing.all()}

            new_products = [
                MerchItemEntity(**product)
                for product in INITIAL_PRODUCTS
                if product["name"] not in existing_names
            ]

            if new_products:
                session.add_all(new_products)
                await session.commit()
                print(f"\033[94m[INFO] Добавлено {len(new_products)} товаров мерча.\033[0m")
            else:
                print("\033[93m[INFO] Новые товары не нужны — все уже есть.\033[0m")

        print("\033[92m[SUCCESS] База данных успешно инициализирована!\033[0m")

    except Exception as e:
        print(f"\033[91m[ERROR] Ошибка при инициализации БД: {e}\033[0m")
        raise
    finally:
        await engine.dispose()