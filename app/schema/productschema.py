from datetime import datetime
from pydantic import BaseModel,Field, field_serializer,field_validator,EmailStr
from fastapi import APIRouter,Form
import re

class ProductBase(BaseModel):
   name:str=Field(...)
   description:str=Field(...)
   price:int=Field(...)
   product_image:str=Field(None)
   sku:str=Field(None)
   stock:int=Field(...)
   unit:str=Field(...)
   is_active:bool=Field(...)
   offer_price:int=Field(None)
   cat_id:int=Field(...)
   

class ProductUpdate(BaseModel):
   name: str = Field(None, min_length=2, max_length=100)
   description: str = Field(None, min_length=2, max_length=255)
   price: int = Field(None, gt=0)
   sku: str = Field(None, min_length=1, max_length=255)
   stock: int = Field(None, ge=0)
   unit: str = Field(None, min_length=1, max_length=50)
   is_active: bool = Field(None)
   offer_price: int = Field(None, gt=0)
   cat_id: int = Field(None, gt=0)


class ProductResponse(BaseModel):
    id:int
    name:str
    description:str
    price:int
    product_image:str
    sku:str
    stock:int
    unit:str
    is_active:int
    offer_price:int
    cat_id:int
    created_at: datetime
    updated_at: datetime
    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")
    model_config = {"from_attributes": True}


# class ProductResponsee(ProductBase):
#     id:int
#     name:str
#     description:str
#     price:int
#     product_image:str
#     sku:str
#     stock:int
#     unit:str
#     is_active:int
#     offer_price:int
#     cat_id:int
#     created_at: datetime
#     updated_at: datetime
#     @field_serializer("created_at", "updated_at")
#     def serialize_datetime(self, value: datetime) -> str:
#         return value.strftime("%Y-%m-%d %H:%M:%S")
#     model_config = {"from_attributes": True}


class CategoryByProductResponse(BaseModel):
    id:int
    cat_name:str
    cat_title:str
    cat_slug:str
    product:list[ProductResponse] | None = None
    model_config = {"from_attributes": True}
