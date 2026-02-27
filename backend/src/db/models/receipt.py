from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Float, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from src.db.base import Base

from src.db.models.user import User


class Receipt(Base):
    """
    ORM model representing a single receipt.
    """

    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    merchant: Mapped[Optional[str]] = mapped_column(String(255))
    total: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    transaction_date: Mapped[Optional[date]] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20))
    blob_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    user = relationship("User", backref="receipts")
    items = relationship(
        "ReceiptItem",
        backref="receipt",
        cascade="all, delete-orphan",
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[Optional[str]] = mapped_column(String(255))
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    price: Mapped[Optional[float]] = mapped_column(Float)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category_source: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    category_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    categorized_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
