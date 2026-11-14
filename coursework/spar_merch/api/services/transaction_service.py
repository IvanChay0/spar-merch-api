from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables.entities.employee import Employee
from database.tables.entities.merch_item import MerchItem
from database.tables.junctions.purchase import Purchase
from database.tables.junctions.transfer import Transfer


async def buy_merch_item(session: AsyncSession, employee: Employee, item_id: UUID) -> dict:
    """Покупка товара. Проверяет баланс, списывает монеты, создает запись."""
    # 1. Находим товар
    result = await session.execute(select(MerchItem).where(MerchItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Товар не найден")

    # 2. Проверяем баланс
    if employee.coins_amount < item.price:
        raise ValueError("Недостаточно монет на счете")

    # 3. Списываем монеты
    employee.coins_amount -= item.price

    # 4. Создаем запись о покупке
    new_purchase = Purchase(employee_id=employee.id, merch_item_id=item.id)
    session.add(new_purchase)

    await session.commit()
    await session.refresh(employee)

    return {"message": f"Товар '{item.name}' успешно куплен", "new_balance": employee.coins_amount}


async def transfer_coins(session: AsyncSession, sender: Employee, gainer_username: str, amount: float) -> dict:
    """Перевод монет другому сотруднику."""
    if amount <= 0:
        raise ValueError("Сумма перевода должна быть больше нуля")

    if sender.coins_amount < amount:
        raise ValueError("Недостаточно монет на счете")

    # Находим получателя
    result = await session.execute(select(Employee).where(Employee.username == gainer_username))
    gainer = result.scalar_one_or_none()

    if not gainer:
        raise ValueError("Сотрудник-получатель не найден")

    if sender.id == gainer.id:
        raise ValueError("Нельзя перевести монеты самому себе")

    # Выполняем перевод
    sender.coins_amount -= amount
    gainer.coins_amount += amount

    # Записываем транзакцию
    new_transfer = Transfer(
        sender_id=sender.id,
        gainer_id=gainer.id,
        amount=amount
    )
    session.add(new_transfer)

    await session.commit()
    await session.refresh(sender)
    await session.refresh(gainer)

    return {"message": f"Успешно переведено {amount} монет сотруднику {gainer.username}"}