from app.config.db import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    cat_name = Column(String(50), nullable=False)
    cat_title = Column(String(100), nullable=False)
    cat_slug = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    create_by = Column(String(100), nullable=True)
    update_by = Column(String(50), nullable=True)