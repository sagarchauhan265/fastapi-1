from datetime import datetime
from pydantic import BaseModel, Field, field_validator, field_serializer
import re

from sqlalchemy import func


class CategoryCreate(BaseModel):
    cat_name: str = Field(..., min_length=2, max_length=50)
    cat_title: str = Field(..., min_length=2, max_length=100)
    cat_slug: str = Field(..., min_length=2, max_length=100)


    @field_validator("cat_slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError("Slug must be lowercase alphanumeric with hyphens only (e.g. 'mobile-phones')")
        return v


class CategoryResponse(BaseModel):
    id: int
    cat_name: str
    cat_title: str
    cat_slug: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    create_by: str | None = None
    update_by: str | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    model_config = {"from_attributes": True}
