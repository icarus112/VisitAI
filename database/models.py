from decimal import Decimal
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Time, Enum, ForeignKey, Date, BigInteger

from app.core import enum
from app.core.enum import BookStatus


class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(12), nullable=False)

    bookings = relationship(
        "Booking", back_populates="users"
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
    status:Mapped[enum.BookStatus] = mapped_column(Enum(BookStatus), default= enum.BookStatus.PENDING, nullable=False)

    users = relationship(
        "User", back_populates="bookings")

    catalogs = relationship(
        "Catalog", back_populates="bookings"
    )

    def __repr__(self):
        return(f"<Booking: id={self.id}, catalog_id={self.catalog_id},"
               f"user_id={self.user_id}, date={self.date}, time={self.time},")

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="admin")
