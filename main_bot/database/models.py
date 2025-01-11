from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, BigInteger
from sqlalchemy.orm import relationship
from .db_session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, index=True)
    full_name = Column(String)
    registration_time = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float, default=0.0)
    frozen_balance = Column(Float, default=0.0)
    partner_balance = Column(Float, default=0.0)
    total_purchases = Column(Integer, default=0)
