from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base

class CatLog(Base):
    __tablename__ = "cat_logs"

    id = Column(Integer, primary_key=True, index=True)
    fact = Column(String, nullable=True)
    neko_url = Column(String, nullable=False)
    http_cat_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())