# schemas.py
from pydantic import BaseModel, constr
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, conint
from sqlalchemy import Float



# Schema for a global ingredient
class Ingredient(BaseModel):
    id: int
    name: constr(min_length=1)
    quantity: conint(ge=0)

    class Config:
        from_attributes = True

# Schema for product-specific ingredients
class IngredientQuantity(BaseModel):
    name: constr(min_length=1)
    quantity: conint(gt=0)

# Schema for a creating an ingredient
class IngredientCreate(BaseModel):
    name: constr(min_length=1)
    quantity: conint(ge=0)

# Schema for updating a product
class IngredientUpdate(BaseModel):
    name: Optional[constr(min_length=1)] = None
    quantity: Optional[int] = None

    class Config:
        from_attributes = True


# Schema for a product, including its specific ingredients
class Product(BaseModel):
    id: int
    name: str
    price: float
    promotion: int
    dietary_type: str
    ingredients: List[IngredientUpdate]

    class Config:
        from_attributes = True

# Schema for creating a product
class ProductCreate(BaseModel):
    name: constr(min_length=1)
    price: float
    promotion: int
    dietary_type: constr(min_length=1)
    ingredients: List[IngredientCreate]


# Schema for updating a product
class ProductUpdate(BaseModel):
    name: Optional[constr(min_length=1)] = None
    price: Optional[float] = None
    promotion: Optional[int] = None
    dietary_type: Optional[constr(min_length=1)] = None
    ingredients: Optional[List[IngredientUpdate]] = None

# # Schema for a product, including its specific ingredients
# class Order(BaseModel):
#     id = Column(Integer, primary_key=True, index=True)
#     order_number = Column(String(20), unique=True, index=True)
#     order_type = Column(String(20), nullable=False)
#     order_status = Column(String(20), nullable=False)
#     order_date = Column(DateTime, nullable=False)
#     ingredients: List[IngredientUpdate]


# class CustomerBase(BaseModel):
#     name: str
#     phone: str
#     address: str
#
# class Customer(CustomerBase):
#     id: int
#
#     class Config:
#         from_attributes = True
#
# class MenuItemBase(BaseModel):
#     name: str
#     ingredients: str
#     price: float
#     calories: int
#     category: str
#
# class MenuItem(MenuItemBase):
#     id: int
#
#     class Config:
#         from_attributes = True
#
# class OrderBase(BaseModel):
#     order_number: str
#     customer_id: int
#     order_type: str
#     order_status: str
#
# class OrderCreate(OrderBase):
#     pass
#
# class Order(OrderBase):
#     id: int
#
#     class Config:
#         from_attributes = True
#
# class OrderItemBase(BaseModel):
#     order_id: int
#     menu_item_id: int
#     quantity: int
#
# class OrderItemCreate(OrderItemBase):
#     pass
#
# class OrderItem(OrderItemBase):
#     id: int
#
#     class Config:
#         from_attributes = True
