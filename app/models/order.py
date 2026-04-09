from app.config.db import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    # pending | confirmed | shipped | delivered | cancelled
    total_amount = Column(Integer, nullable=False)
    shipping_address = Column(String(500), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    # Snapshot product details so history stays accurate if product changes
    product_name = Column(String(100), nullable=False)
    product_sku = Column(String(255), nullable=False)
    unit_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
