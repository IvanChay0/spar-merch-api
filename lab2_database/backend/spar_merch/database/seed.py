import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import random
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config import get_settings
from core.security import get_password_hash
from database.tables.entities.employee import Employee
from database.tables.entities.merch_item import MerchItem
from database.tables.junctions.purchase import Purchase
from database.tables.junctions.transfer import Transfer

# Тестовые данные сотрудников
TEST_EMPLOYEES = [
    {"username": "ivan_manager", "password": "password123", "email": "ivan@spar.ru", "phone": "+79001111111"},
    {"username": "maria_cashier", "password": "password123", "email": "maria@spar.ru", "phone": "+79002222222"},
    {"username": "alex_stock", "password": "password123", "email": "alex@spar.ru", "phone": "+79003333333"},
    {"username": "olga_hr", "password": "password123", "email": "olga@spar.ru", "phone": "+79004444444"},
    {"username": "dmitry_director", "password": "password123", "email": "dmitry@spar.ru", "phone": "+79005555555"},
]


async def seed_database():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    async with AsyncSession(engine) as session:
        print("🔍 Проверка наличия тестовых данных...")

        # 1. Проверяем, есть ли уже тестовые сотрудники
        result = await session.execute(select(Employee).where(Employee.username == "ivan_manager"))
        if result.scalar_one_or_none():
            print("⚠️ Тестовые данные уже существуют. Пропускаем сидинг.")
            return

        print("👥 Создание 5 тестовых сотрудников...")
        employee_ids = []  # Храним только UUID, чтобы избежать MissingGreenlet после commit

        for emp_data in TEST_EMPLOYEES:
            emp_id = uuid4()  # Генерируем ID явно
            new_emp = Employee(
                id=emp_id,
                username=emp_data["username"],
                password=get_password_hash(emp_data["password"]),
                email=emp_data["email"],
                phone=emp_data["phone"],
                coins_amount=5000.0
            )
            session.add(new_emp)
            employee_ids.append(emp_id)

        await session.commit()
        print(f"✅ Создано {len(employee_ids)} сотрудников.")

        # 2. Получаем список товаров
        items_result = await session.execute(select(MerchItem))
        items = items_result.scalars().all()
        if not items:
            print("❌ Ошибка: В базе нет товаров! Сначала запустите start.py")
            return

        print("🛒 Генерация 30 случайных покупок...")
        for _ in range(30):
            buyer_id = random.choice(employee_ids)
            item = random.choice(items)

            # Атомарное списание через Core (без обращения к ORM-объектам)
            await session.execute(
                update(Employee)
                .where(Employee.id == buyer_id)
                .values(coins_amount=Employee.coins_amount - item.price)
            )

            # Создаем запись о покупке
            purchase = Purchase(employee_id=buyer_id, merch_item_id=item.id)
            session.add(purchase)

        await session.commit()
        print("✅ Покупки созданы.")

        print("💸 Генерация 15 случайных переводов...")
        for _ in range(15):
            sender_id = random.choice(employee_ids)
            possible_gainers = [eid for eid in employee_ids if eid != sender_id]
            gainer_id = random.choice(possible_gainers)

            amount = round(random.uniform(10.0, 100.0), 2)

            # Атомарное списание у отправителя
            await session.execute(
                update(Employee)
                .where(Employee.id == sender_id)
                .values(coins_amount=Employee.coins_amount - amount)
            )
            # Атомарное начисление получателю
            await session.execute(
                update(Employee)
                .where(Employee.id == gainer_id)
                .values(coins_amount=Employee.coins_amount + amount)
            )

            # Создаем запись о переводе
            transfer = Transfer(sender_id=sender_id, gainer_id=gainer_id, amount=amount)
            session.add(transfer)

        await session.commit()
        print("✅ Переводы созданы.")

    await engine.dispose()
    print("\n🎉 База данных успешно наполнена тестовыми данными!")


if __name__ == "__main__":
    print("=" * 50)
    print("  Spar Merch API — Наполнение БД тестовыми данными")
    print("=" * 50)
    asyncio.run(seed_database())