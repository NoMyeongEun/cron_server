from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, JSON
from .database import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    hashed_password = Column(String)
    gender = Column(String)
    goal = Column(JSON)