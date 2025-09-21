from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

class IssueStatusEnum(str, enum.Enum):
    Pending = "Pending"
    InProgress = "In Progress"
    Resolved = "Resolved"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Email is now optional (nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    # Phone number is now included, also optional and unique
    phone_number = Column(String, unique=True, index=True, nullable=True)
    
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)

    issues = relationship("Issue", back_populates="owner")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    department = Column(String, index=True)
    photo_url = Column(String)
    audio_url = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(Enum(IssueStatusEnum), default=IssueStatusEnum.Pending)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="issues")