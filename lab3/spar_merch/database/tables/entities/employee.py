from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Uuid, Float

from database.base import Base

if TYPE_CHECKING:
    from database.tables.junctions.purchase import Purchase
    from database.tables.junctions.transfer import Transfer


class Employee(Base):
    """Сущность 'Сотрудник' — основной пользователь системы Spar Merch."""
    __tablename__ = "employee"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="employee_pkey"),
        UniqueConstraint("username", name="employee_username_uk"),
        UniqueConstraint("email", name="employee_email_uk"),
        UniqueConstraint("phone", name="employee_phone_uk"),
        {"comment": "Таблица записей о сотрудниках."},
    )

    id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4)
    username: Mapped[str] = mapped_column(String(256))
    password: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256), nullable=True)
    phone: Mapped[str] = mapped_column(String(256), nullable=True)
    coins_amount: Mapped[float] = mapped_column(Float(), nullable=False, default=1000.0)
    refresh_token: Mapped[str] = mapped_column(String(256), nullable=True)

    # Связь 1:M с покупками
    purchases: Mapped[List["Purchase"]] = relationship(
        "Purchase", back_populates="employee"
    )
    # Связь M:M с товарами (через purchase)
    bought_items: Mapped[List["MerchItem"]] = relationship(
        "MerchItem", secondary="purchase", viewonly=True,
    )
    # Исходящие переводы
    sent_transfers: Mapped[List["Transfer"]] = relationship(
        "Transfer", foreign_keys="[Transfer.sender_id]",
        back_populates="sender",
    )
    # Входящие переводы
    gained_transfers: Mapped[List["Transfer"]] = relationship(
        "Transfer", foreign_keys="[Transfer.gainer_id]",
        back_populates="gainer",
    )

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, username={self.username}, coins={self.coins_amount})>"