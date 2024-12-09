# schemas.py
from datetime import datetime, date

from pydantic import BaseModel, constr, validator, field_validator
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, conint
from sqlalchemy import Float



# Schema for a global ingredient
class Ingredient(BaseModel):
    id: Optional[int]
    name: constr(min_length=1)
    quantity: conint(ge=0)

    class Config:
        from_attributes = True

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

class Order(BaseModel):
    id: int
    order_type: str
    order_status: str
    order_date: date  # Use `date` for the field
    products: List[ProductUpdate]

    @field_validator("order_date", mode="before")
    def validate_order_date(cls, value):
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")
        elif isinstance(value, date):
            return value
        else:
            raise ValueError("Invalid date type. Must be a date or ISO8601 string.")

    class Config:
        from_attributes = True

class CreateOrder(BaseModel):
    order_type: str = Field(pattern="^(takeout|delivery)$")  # Restrict to "takeout" or "delivery"
    order_status: str = Field(pattern="^(finished|prepping|payed)$")  # Restrict to "finished", "prepping" or "paid"
    product_ids: List[int]  # List of product IDs

    class Config:
        from_attributes = True

class Review(BaseModel):
    id: int
    product_id: int
    title: str
    description: str

    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    product_id: conint(ge=1)
    title: Optional[constr(min_length=1)] = None
    description: Optional[constr(min_length=1)] = None

    class Config:
        from_attributes = True

class CreateReview(BaseModel):
    product_id: conint(ge=1)
    title: constr(min_length=1)
    description: constr(min_length=1)

    class Config:
        from_attributes = True

class PromoCodeBase(BaseModel):
    code: str
    discount_percentage: float
    expiration_date: date
    is_active: bool = True

    class Config:
        from_attributes = True


class CreatePromoCode(PromoCodeBase):
    pass


class PromoCodeResponse(PromoCodeBase):
    id: int

class OrderWithDiscount(Order):
    discounted_total: float
