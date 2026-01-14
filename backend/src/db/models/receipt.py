from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Float, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from src.db.base import Base


class Receipt(Base):
    """
    ORM model representing a single receipt.
    """

    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant: Mapped[Optional[str]] = mapped_column(String(255))
    total: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    transaction_date: Mapped[Optional[date]] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    items = relationship(
        "ReceiptItem",
        backref="receipt",
        cascade="all, delete-orphan",
    )
