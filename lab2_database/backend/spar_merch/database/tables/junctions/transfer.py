from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, Float, DateTime

from database.base import Base

if TYPE_CHECKING:
    from database.tables.entities.employee import Employee


class Transfer(Base):
    """Сущность 'Перевод монет' между двумя сотрудниками."""
    __tablename__ = "transfer"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="transfer_pkey"),
        ForeignKeyConstraint(
            ["sender_id"], ["employee.id"],
            name="transfer_sender_id_fk",
            onupdate="CASCADE", ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["gainer_id"], ["employee.id"],
            name="transfer_gainer_id_fk",
            onupdate="CASCADE", ondelete="CASCADE",
        ),
        {"comment": "Таблица с записями о переводах монет."},
    )

    id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4)
    sender_id: Mapped[UUID] = mapped_column(Uuid())
    gainer_id: Mapped[UUID] = mapped_column(Uuid())
    amount: Mapped[float] = mapped_column(Float(), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    sender: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[sender_id], back_populates="sent_transfers"
    )
    gainer: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[gainer_id], back_populates="gained_transfers"
    )

    def __repr__(self) -> str:
        return f"<Transfer(sender={self.sender_id}, gainer={self.gainer_id}, amount={self.amount})>"