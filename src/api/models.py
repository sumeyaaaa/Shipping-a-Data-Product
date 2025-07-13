from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = "fct_messages"
    message_id = Column(Integer, primary_key=True, index=True)
    channel = Column(Text, index=True)
    message_date = Column(DateTime)
    message_text = Column(Text)