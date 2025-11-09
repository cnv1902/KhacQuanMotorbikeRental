"""SQLAlchemy models for KhacQuanMotorbikeRental.

Includes models for:
 - StoreInfo
 - Article
 - Motorcycle
 - DetailMotorcycle
 - Customer
 - Rental
 - RentalItem
 - Payment

Run this file directly to create tables using DATABASE_URL from .env.
"""
from datetime import datetime
from decimal import Decimal
import os

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,
    create_engine,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_LOCAL")

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Accounts(Base, TimestampMixin):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Account id={self.id} username={self.username!r}>"

class StoreInfo(Base, TimestampMixin):
    __tablename__ = "store_info"

    id = Column(Integer, primary_key=True)
    store_name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    business_hours = Column(String(255), nullable=True)
    google_map_url = Column(String(1000), nullable=True)
    slide_url = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<StoreInfo id={self.id} name={self.store_name!r}>"


class Article(Base, TimestampMixin):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    featured_image = Column(String(1000), nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Article id={self.id} title={self.title!r}>"


class Motorcycle(Base, TimestampMixin):
    __tablename__ = "motorcycle"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, nullable=True)
    brand = Column(String(255), nullable=True)
    engine_capacity = Column(String(50), nullable=True)
    price_per_day = Column(Numeric(10, 2), nullable=True)
    price_per_week = Column(Numeric(10, 2), nullable=True)
    price_per_month = Column(Numeric(10, 2), nullable=True)
    image = Column(String(1000), nullable=True)

    details = relationship("DetailMotorcycle", back_populates="motorcycle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Motorcycle id={self.id} name={self.name!r}>"


class DetailMotorcycle(Base, TimestampMixin):
    __tablename__ = "detail_motorcycle"

    id = Column(Integer, primary_key=True)
    motorcycle_id = Column(Integer, ForeignKey("motorcycle.id", ondelete="CASCADE"), nullable=False)
    license_plate = Column(String(100), nullable=False, unique=True)
    model_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)

    motorcycle = relationship("Motorcycle", back_populates="details")

    def __repr__(self):
        return f"<DetailMotorcycle id={self.id} plate={self.license_plate!r}>"


class Customer(Base, TimestampMixin):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    hometown = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    citizen_id = Column(String(100), nullable=True, unique=True)
    citizen_id_front_image = Column(String(1000), nullable=True)
    citizen_id_back_image = Column(String(1000), nullable=True)
    driver_license_number = Column(String(100), nullable=True)
    driver_license_image = Column(String(1000), nullable=True)

    rentals = relationship("Rental", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer id={self.id} name={self.full_name!r}>"


class Rental(Base, TimestampMixin):
    __tablename__ = "rental"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    actual_return_date = Column(DateTime, nullable=True)
    rental_days = Column(Integer, nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True, default=Decimal("0.00"))
    deposit_amount = Column(Numeric(12, 2), nullable=True, default=Decimal("0.00"))
    paid_amount = Column(Numeric(12, 2), nullable=True, default=Decimal("0.00"))
    status = Column(String(50), nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), nullable=True)
    vnpay_transaction_id = Column(String(255), nullable=True)
    vnpay_bank_code = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="rentals")
    items = relationship("RentalItem", back_populates="rental", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="rental", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rental id={self.id} customer_id={self.customer_id} status={self.status!r}>"


class RentalItem(Base):
    __tablename__ = "rental_item"

    id = Column(Integer, primary_key=True)
    rental_id = Column(Integer, ForeignKey("rental.id", ondelete="CASCADE"), nullable=False)
    motorcycle_id = Column(Integer, ForeignKey("detail_motorcycle.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price_per_day = Column(Numeric(12, 2), nullable=True)
    sub_total = Column(Numeric(12, 2), nullable=True)

    rental = relationship("Rental", back_populates="items")
    motorcycle = relationship("DetailMotorcycle")

    def __repr__(self):
        return f"<RentalItem id={self.id} rental_id={self.rental_id} motorcycle_id={self.motorcycle_id}>"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True)
    rental_id = Column(Integer, ForeignKey("rental.id", ondelete="SET NULL"), nullable=True)
    payment_code = Column(String(255), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    payment_method = Column(String(100), nullable=True)
    payment_status = Column(String(100), nullable=True)
    vnpay_transaction_id = Column(String(255), nullable=True)
    vnpay_bank_code = Column(String(100), nullable=True)
    vnpay_pay_date = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)

    rental = relationship("Rental", back_populates="payments")

    def __repr__(self):
        return f"<Payment id={self.id} rental_id={self.rental_id} amount={self.amount}>"


# helpful indexes
Index("ix_detail_motorcycle_license", DetailMotorcycle.license_plate)


def create_tables(url=None):
    """Create all tables using the provided DATABASE_URL or the env var."""
    connect_url = url or DATABASE_URL
    if not connect_url:
        raise RuntimeError("DATABASE_URL not configured in environment")
    engine = create_engine(connect_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    print("DATABASE_URL:", bool(DATABASE_URL))
    if not DATABASE_URL:
        print("Không tìm thấy DATABASE_URL trong .env — vui lòng thiết lập trước khi chạy tạo bảng.")
    else:
        engine = create_tables()
        print("Bảng đã được tạo (nếu chưa tồn tại).")
