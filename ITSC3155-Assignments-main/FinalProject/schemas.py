# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class CustomerBase(BaseModel):
    name: str
    phone: str
    address: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class MenuItemBase(BaseModel):
    name: str
    ingredients: str
    price: float
    calories: int
    category: str

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    order_number: str
    customer_id: int
    order_type: str
    order_status: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        orm_mode = True

class OrderItemBase(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int

    class Config:
        orm_mode = True
