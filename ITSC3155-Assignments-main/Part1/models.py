# models.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, JSON, DateTime, CheckConstraint, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    quantity = Column(Integer)

order_products = Table(
    "order_products",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("quantity", Integer, nullable=False, default=1),  # Add quantity
)


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
    order_status = Column(Enum("finished", "prepping", name="order_status_enum"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    products = Column(JSON, nullable=False)  # Add the products column as JSON


# class OrderItem(Base):
#     __tablename__ = "order_items"
#
#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
#     quantity = Column(Integer)
#     order = relationship("Order", back_populates="items")
#     menu_item = relationship("MenuItem")
