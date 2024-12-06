# schemas.py

from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from enums import CategoryEnum
from pydantic import BaseModel, Field
from typing import List, Annotated
from enums import OrderTypeEnum, OrderStatusEnum

# Remove redundant Enum Definitions

# Customer Schemas
class CustomerBase(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: str

class Customer(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# MenuItem Schemas
class MenuItemBase(BaseModel):
    name: str
    ingredients: str
    price: float
    calories: int
    category: CategoryEnum  # Use imported Enum

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int

    class Config:
        from_attributes = True  # Updated

# OrderItem Schemas
class OrderItemBase(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int
    total_amount: float

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItem(OrderItemBase):
    id: int
    menu_item: Optional[MenuItem] = None  # Include menu item details if needed

    class Config:
        from_attributes = True  # Updated

# Order Schemas
class OrderBase(BaseModel):
    order_number: str
    customer_id: int
    order_type: OrderTypeEnum  # Use imported Enum
    order_status: OrderStatusEnum  # Use imported Enum
    total_amount: float = 0.0

class OrderCreate(BaseModel):
    order_number: str
    customer: CustomerCreate  # Customer details are required
    order_type: OrderTypeEnum
    order_status: OrderStatusEnum
    total_amount: float
    items: Annotated[List[OrderItemCreate], Field(default_factory=list)]

class Order(OrderBase):
    id: int
    items: Annotated[List[OrderItem], Field(default_factory=list)]  # Updated

    class Config:
        from_attributes = True  # Updated

# Payment Schemas
class PaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_method: str
    payment_status: str

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # Updated

# Promotion Schemas
class PromotionBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_percentage: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True

class PromotionCreate(PromotionBase):
    pass

class Promotion(PromotionBase):
    id: int

    class Config:
        from_attributes = True  # Updated

# Feedback Schemas
class FeedbackBase(BaseModel):
    customer_id: int
    order_id: int
    rating: int
    comments: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # Updated

# TrainingMaterial Schemas
class TrainingMaterialBase(BaseModel):
    title: str
    content: str

class TrainingMaterialCreate(TrainingMaterialBase):
    pass

class TrainingMaterial(TrainingMaterialBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated

# OrderUpdate Schema
class OrderUpdate(BaseModel):
    order_type: Optional[OrderTypeEnum] = None  # Use imported Enum
    order_status: Optional[OrderStatusEnum] = None  # Use imported Enum

    class Config:
        from_attributes = True  # Updated

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float

class MenuItem(BaseModel):
    id: int
    name: str
    description: str
    price: float

    class Config:
        orm_mode = True
