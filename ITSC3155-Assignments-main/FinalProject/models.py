# models.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    phone = Column(String(15))
    address = Column(String(100))
    orders = relationship("Order", back_populates="customer")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    ingredients = Column(String(255))
    price = Column(Float)
    calories = Column(Integer)
    category = Column(Enum("spicy", "kids", "vegetarian", "low fat", "regular"))

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_type = Column(Enum("take-out", "delivery"))
    order_status = Column(Enum("placed", "in-progress", "completed"))
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
