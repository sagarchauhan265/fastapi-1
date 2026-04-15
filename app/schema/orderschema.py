from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer


class PlaceOrderRequest(BaseModel):
    shipping_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    unit_price: int
    quantity: int
    subtotal: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    name:str
    email:str
    status: str
    total_amount: int
    shipping_address: Optional[str]
    notes: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    model_config = {"from_attributes": True}


class OrderSummaryResponse(BaseModel):
    id: int
    name:str
    email:str
    status: str
    total_amount: int
    item_count: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: List[OrderSummaryResponse]
    total: int
    page: int
    page_size: int

class CheckoutResponse(BaseModel):
    order_id: int
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class UserOrderSummaryResponse(BaseModel):
    id: int
    status: str
    products: List[OrderSummaryResponse]
    total_amount: int
    item_count: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    model_config = {"from_attributes": True}   
