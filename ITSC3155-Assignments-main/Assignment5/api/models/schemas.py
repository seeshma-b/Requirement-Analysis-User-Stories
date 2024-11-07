from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SandwichBase(BaseModel):
    sandwich_name: str
    price: float


class SandwichCreate(SandwichBase):
    pass


class SandwichUpdate(BaseModel):
    sandwich_name: Optional[str] = None
    price: Optional[float] = None


class Sandwich(SandwichBase):
    id: int

    class ConfigDict:
        from_attributes = True


class ResourceBase(BaseModel):
    item: str
    amount: int


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    item: Optional[str] = None
    amount: Optional[int] = None


class Resource(ResourceBase):
    id: int

    class ConfigDict:
        from_attributes = True


class RecipeBase(BaseModel):
    amount: int


class RecipeCreate(RecipeBase):
    sandwich_id: int
    resource_id: int

class RecipeUpdate(BaseModel):
    sandwich_id: Optional[int] = None
    resource_id: Optional[int] = None
    amount: Optional[int] = None

class Recipe(RecipeBase):
    id: int
    sandwich: Sandwich = None
    resource: Resource = None

    class ConfigDict:
        from_attributes = True


class OrderDetailBase(BaseModel):
    amount: int


class OrderDetailCreate(OrderDetailBase):
    order_id: int
    sandwich_id: int

class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    sandwich_id: Optional[int] = None
    amount: Optional[int] = None


class OrderDetail(OrderDetailBase):
    id: int
    order_id: int
    sandwich: Sandwich = None

    class ConfigDict:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str
    description: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    description: Optional[str] = None


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: list[OrderDetail] = None

    class ConfigDict:
        from_attributes = True
