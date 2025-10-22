from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Date, DateTime, Numeric, ForeignKey, Text,
    Index, func
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Owner(Base):
    __tablename__ = "owner"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    cars: Mapped[list["Car"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Owner(id={self.id}, name={self.name})"


class Car(Base):
    __tablename__ = "car"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    make: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    year_of_manufacture: Mapped[int | None] = mapped_column(Integer)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("owner.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    owner: Mapped["Owner"] = relationship(back_populates="cars")
    policies: Mapped[list["InsurancePolicy"]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )
    claims: Mapped[list["Claim"]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )

    __table_args__ = ()


class InsurancePolicy(Base):
    __tablename__ = "insurance_policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(
        ForeignKey("car.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    # IMPORTANT: initially nullable=True to allow data migration (Task A),
    # later we'll set NOT NULL via a separate Alembic migration.
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # chosen approach for de-dup: single nullable column rather than a log table
    logged_expiry_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False))

    car: Mapped["Car"] = relationship(back_populates="policies")

    __table_args__ = ()


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(
        ForeignKey("car.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    car: Mapped["Car"] = relationship(back_populates="claims")

    __table_args__ = ()
