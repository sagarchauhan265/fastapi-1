from app.config.db import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Integer, nullable=False)
    product_image = Column(String(255), nullable=True)  # Store image path or URL
    sku = Column(String(255),unique=True, nullable=False)  # New SKU column
    stock  = Column(Integer, nullable=False, )  # New stock column
    unit = Column(String(50), nullable=False, )  # New unit
    is_active = Column(Integer, nullable=False, )  # New is_active column (1 for active, 0 for inactive)
    offer_price = Column(Integer, nullable=True)  # New offer price column
    cat_id = Column(Integer, nullable=False)  # New category ID column
    currency = Column(String(10), nullable=False, default="INR")  # New currency column
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
