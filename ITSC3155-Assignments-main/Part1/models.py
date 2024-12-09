# models.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, JSON, DateTime, CheckConstraint, Table, Date, \
    Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    quantity = Column(Integer)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    price = Column(Float, nullable=False)
    promotion = Column(Integer, nullable=False)
    dietary_type = Column(String(255), nullable=False)
    ingredients = Column(JSON, nullable=False)  # Store ingredients as JSON

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_type = Column(Enum("takeout", "delivery", name="order_type_enum"), nullable=False)
    order_status = Column(Enum("finished", "prepping", "paid", name="order_status_enum"), nullable=False)
    order_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    products = Column(JSON, default=[])  # Default to an empty list



class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255))


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    expiration_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
