from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables.entities.employee import Employee
from database.tables.entities.merch_item import MerchItem
from database.tables.junctions.purchase import Purchase


async def get_employee_by_id(session: AsyncSession, employee_id: UUID) -> Employee | None:
    result = await session.execute(select(Employee).where(Employee.id == employee_id))
    return result.scalar_one_or_none()


async def get_employee_inventory(session: AsyncSession, employee_id: UUID) -> list[dict]:
    """Возвращает список купленных товаров с датами покупок."""
    # Используем selectinload для эффективной загрузки связанных данных (JOIN)
    stmt = (
        select(Purchase, MerchItem)
        .join(MerchItem, Purchase.merch_item_id == MerchItem.id)
        .where(Purchase.employee_id == employee_id)
        .order_by(Purchase.date.desc())
    )
    result = await session.execute(stmt)
    records = result.all()

    return [
        {
            "purchase_id": str(purchase.id),
            "date": purchase.date.isoformat(),
            "item_name": merch.name,
            "price": merch.price
        }
        for purchase, merch in records
    ]