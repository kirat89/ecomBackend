from pydantic import BaseModel
from typing import List, Optional

class CreateProduct(BaseModel):
    name: str
    description: str
    specifications: str
    category: str
    no_of_stock: int
    price_per_stock: float
    images: Optional[List[str]] = []

class UpdateProduct(BaseModel):
    name: str
    description: str
    specifications: str
    category: str
    no_of_stock: int
    price_per_stock: float
    soft_delete: Optional[bool] = False
    archived: Optional[bool] = False

class UpdateProductQuantity(BaseModel):
    quantity:int   
    




