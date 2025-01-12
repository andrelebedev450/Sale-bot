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
    
    referral_code = Column(String, unique=True, index=True)
    invited_count = Column(Integer, default=0)
    total_earned = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)

    tickets = relationship("SupportTicket", order_by="SupportTicket.id", back_populates="user")

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    topic = Column(String)
    message = Column(String)
    status = Column(String, default="На рассмотрении")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tickets")
