# models.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, JSON, DateTime, CheckConstraint
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

    # Store ingredients as JSON
    ingredients = Column(JSON, nullable=False)  # JSON column to store ingredient details


# class Order(Base):
#     __tablename__ = "orders"
#
#     id = Column(Integer, primary_key=True, index=True)
#     order_number = Column(String(20), unique=True, index=True)
#     order_type = Column(String(20), nullable=False)
#     order_status = Column(String(20), nullable=False)
#     order_date = Column(DateTime, nullable=False)
#
#     __table_args__ = (
#         CheckConstraint(
#             "order_type IN ('takeout', 'delivery')",
#             name="check_order_type"
#         ),
#         CheckConstraint(
#             "order_status IN ('finished', 'prepping')",
#             name="check_order_status"
#         ),
#     )
# #
# class OrderItem(Base):
#     __tablename__ = "order_items"
#
#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
#     quantity = Column(Integer)
#     order = relationship("Order", back_populates="items")
#     menu_item = relationship("MenuItem")
