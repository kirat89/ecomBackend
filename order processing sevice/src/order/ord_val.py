from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    customer_id: int
    items: List[OrderItem]
    total_amount: float
    order_date: datetime
    status: str

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]
