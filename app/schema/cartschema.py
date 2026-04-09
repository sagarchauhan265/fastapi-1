from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_serializer
from fastapi import BackgroundTasks

from app.schema.productschema import ProductResponse


class AddToCartRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: int
    quantity: int
    subtotal: int
    product: ProductResponse | None = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: int
