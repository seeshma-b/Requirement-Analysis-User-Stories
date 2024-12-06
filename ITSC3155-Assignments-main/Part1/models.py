
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

# Import Enums from enums.py
from enums import OrderTypeEnum, OrderStatusEnum, CategoryEnum

Base = declarative_base()

# Define Models
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    price = Column(Float)

    order_items = relationship("OrderItem", back_populates="menu_item")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    phone = Column(String(15))
    address = Column(String(100))

    orders = relationship("Order", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_type = Column(Enum(OrderTypeEnum))
    order_status = Column(Enum(OrderStatusEnum))
    total_amount = Column(Float)

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    total_amount = Column(Float)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float)
    payment_method = Column(String(50))
    payment_status = Column(String(50))

    order = relationship("Order", back_populates="payments")

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)
    description = Column(String(255))
    discount_percentage = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer)
    comments = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedbacks")

class TrainingMaterial(Base):
    __tablename__ = "training_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)


