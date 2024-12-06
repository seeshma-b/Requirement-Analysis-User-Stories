# enums.py

from enum import Enum

class OrderTypeEnum(str, Enum):
    take_out = "take-out"
    delivery = "delivery"

class OrderStatusEnum(str, Enum):
    placed = "placed"
    in_progress = "in-progress"
    completed = "completed"

class CategoryEnum(str, Enum):
    spicy = "spicy"
    kids = "kids"
    vegetarian = "vegetarian"
    low_fat = "low fat"
    regular = "regular"
