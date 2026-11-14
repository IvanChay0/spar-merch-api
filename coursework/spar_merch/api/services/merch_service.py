from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables.entities.merch_item import MerchItem
from schemas.merch import MerchItemCreate, MerchItemUpdate


class MerchService:
    """DAO-слой для работы с товарами мерча."""

    @staticmethod
    async def get_all(session: AsyncSession, limit: int = 100) -> list[MerchItem]:
        result = await session.execute(select(MerchItem).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(session: AsyncSession, item_id: UUID) -> MerchItem | None:
        result = await session.execute(
            select(MerchItem).where(MerchItem.id == item_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, item_data: MerchItemCreate) -> MerchItem:
        new_item = MerchItem(**item_data.model_dump())
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item

    @staticmethod
    async def update(
        session: AsyncSession, item_id: UUID, item_data: MerchItemUpdate
    ) -> MerchItem | None:
        item = await MerchService.get_by_id(session, item_id)
        if not item:
            return None
        for key, value in item_data.model_dump().items():
            setattr(item, key, value)
        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def delete(session: AsyncSession, item_id: UUID) -> bool:
        item = await MerchService.get_by_id(session, item_id)
        if not item:
            return False
        await session.delete(item)
        await session.commit()
        return True