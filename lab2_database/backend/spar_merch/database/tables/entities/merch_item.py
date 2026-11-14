from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Uuid, Float

from database.base import Base

if TYPE_CHECKING:
    from database.tables.junctions.purchase import Purchase


class MerchItem(Base):
    """Сущность 'Товар мерча' — элемент каталога Spar."""
    __tablename__ = "merch_item"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="merch_item_pkey"),
        {"comment": "Таблица записей о товарах мерча."},
    )

    id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="Описание товара"
    )

    purchases: Mapped[List["Purchase"]] = relationship(
        "Purchase", back_populates="merch_item"
    )

    def __repr__(self) -> str:
        return f"<MerchItem(id={self.id}, name={self.name}, price={self.price})>"