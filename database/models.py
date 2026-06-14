from decimal import Decimal
from datetime import date, time, datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Time, Enum, ForeignKey, Date, BigInteger, DateTime, func, Index, TEXT, JSON
from pgvector.sqlalchemy import Vector

from app.core import enum
from app.core.enum import BookStatus



class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), default="-")

    bookings = relationship(
        "Booking", back_populates="users",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return(f"<User: id={self.id}, name={self.name},"
               f" phone={self.phone}>")

class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column((Numeric(8, 2)),nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    client_phrases: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)

    __table_args__ = (Index("idx_ct_name", "name"),)

    bookings = relationship(
        "Booking", back_populates="catalogs"
    )

    def __repr__(self):
        return(f"<Catalog: id={self.id}, name={self.name},"
               f" price={self.price}, duration={self.duration}>")

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalogs.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date ,nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default= enum.BookStatus.PENDING, nullable=False)
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    comment: Mapped[str] = mapped_column(TEXT, nullable=True)

    users = relationship(
        "User", back_populates="bookings")

    catalogs = relationship(
        "Catalog", back_populates="bookings"
    )

    pay_histories = relationship(
        "PayHistory", back_populates="bookings"
    )

    # здесь добавил индексацию для некоторых полей для ускорения поиска
    __table_args__ = (
        Index("idx_bk_us_id", "user_id"),
        Index("idx_bk_ct_id", "catalog_id"),
        Index("idx_bk_payment_id", "payment_id"),
    )
    def __repr__(self):
        return(f"<Booking: id={self.id}, catalog_id={self.catalog_id},"
               f"user_id={self.user_id}, date={self.date}, time={self.time}>")

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="admin")

class PayHistory(Base):
    __tablename__ = "pay_histories"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    payed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column((Numeric(8, 2)),nullable=False)

    bookings = relationship(
        "Booking", back_populates="pay_histories"
    )

    def __repr__(self):
        return(f"<PayHistory: id={self.id}, booking_id={self.booking_id},"
               f"payed_at={self.payed_at}, amount={self.amount}>")

class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    question: Mapped[str] = mapped_column(TEXT, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    answer: Mapped[str] = mapped_column(TEXT, nullable=False)


