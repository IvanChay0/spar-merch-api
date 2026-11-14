from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, DateTime

from database.base import Base

if TYPE_CHECKING:
    from database.tables.entities.employee import Employee
    from database.tables.entities.merch_item import MerchItem


class Purchase(Base):
    """Связующая таблица 'Покупка' — реализует M:M между Employee и MerchItem."""
    __tablename__ = "purchase"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="purchase_pkey"),
        ForeignKeyConstraint(
            ["employee_id"], ["employee.id"],
            name="purchase_employee_id_fk",
            onupdate="CASCADE", ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["merch_item_id"], ["merch_item.id"],
            name="purchase_merch_item_id_fk",
            onupdate="CASCADE", ondelete="CASCADE",
        ),
        {"comment": "Таблица с записями о покупках."},
    )

    id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(Uuid())
    merch_item_id: Mapped[UUID] = mapped_column(Uuid())
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped["Employee"] = relationship("Employee", back_populates="purchases")
    merch_item: Mapped["MerchItem"] = relationship("MerchItem", back_populates="purchases")

    def __repr__(self) -> str:
        return f"<Purchase(employee_id={self.employee_id}, merch_item_id={self.merch_item_id})>"