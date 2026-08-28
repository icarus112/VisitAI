from decimal import Decimal
from datetime import date, time, datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Time, Enum, ForeignKey, Date, BigInteger, DateTime, func, Index, Text, JSON
from pgvector.sqlalchemy import Vector

from app.core import enum
from app.core.enum import BookStatus, PaymentMethod, PaymentStatus, AdminRole


class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True)
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False)
    phone: Mapped[str] = mapped_column(
        String(15),
        default="-")

    bookings = relationship(
        "Booking", back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return(f"<User: id={self.id}, name={self.name},"
               f" phone={self.phone}>")

class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False)
    price: Mapped[Decimal] = mapped_column(
        (Numeric(8, 2)),
        nullable=False)
    duration: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False)
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False)
    keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False)
    client_phrases: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False)

    __table_args__ = (Index("idx_ct_name", "name"),)

    bookings = relationship(
        "Booking", back_populates="catalog"
    )

    def __repr__(self):
        return(f"<Catalog: id={self.id}, name={self.name},"
               f" price={self.price}, duration={self.duration}>")

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True)
    catalog_id: Mapped[int] = mapped_column(
        ForeignKey("catalogs.id"),
        nullable=False,
        index=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        (Numeric(8, 2)),
        nullable=False)
    status: Mapped[BookStatus] = mapped_column(
        Enum(BookStatus,
             name="book_status",
             value_callable=lambda enum_class: [
                 item.value for item in enum_class
             ]),
        nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod,
             name="payment_method",
             value_callable=lambda enum_class: [
             item.value for item in enum_class
             ]),
        default=enum.PaymentMethod.PENDING,
        nullable=False)

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True)

    user = relationship(
        "User", back_populates="bookings")

    catalog = relationship(
        "Catalog", back_populates="bookings"
    )

    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(
        "PaymentAttempt",
        back_populates="booking",
    )

    # здесь добавил индексацию для некоторых полей для ускорения поиска
    __table_args__ = (
        Index(
            "idx_bookings_catalog_scheduled_at",
            "catalog_id",
            "scheduled_at",
        ),
    )
    def __repr__(self):
        return(f"<Booking: id={self.id}, catalog_id={self.catalog_id},"
               f"user_id={self.user_id}, date={self.scheduled_at.date()}, time={self.scheduled_at.time()}>")

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(
        primary_key=True)
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole,
             name="admin_role",
             value_callable=lambda enum_class: [
                 item.value for item in enum_class
             ]),
        default=enum.AdminRole.ADMIN,
        nullable=False)

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"),
                                            nullable=False, index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(99),
        unique=True,
        nullable=True
    )
    idempotence_key: Mapped[str] = mapped_column(
        String(67),
        unique=True,
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        (Numeric(8, 2)),
        nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        nullable=False,
        default= enum.PaymentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    booking = relationship(
        "Booking", back_populates="payment_attempts"
    )

    __table_args__ = (
        Index("idx_payatt_bk_id", "booking_id"),
    )

    def __repr__(self):
        return(f"<PayHistory: id={self.id}, booking_id={self.booking_id},"
               f"payed_at={self.paid_at}, amount={self.price}>")

class Faq(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("idx_faq_search_text", "search_text"),
    )