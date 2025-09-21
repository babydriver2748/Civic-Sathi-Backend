from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# This defines the data required to create a user.
class UserCreate(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str
    full_name: str

# This defines the data that will be sent back after a user is created.
# Notice it does NOT include the password, for security.
class User(BaseModel):
    id: int
    email: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: str

    class Config:
        orm_mode = True
# This defines the shape of the response when a user logs in successfully.
class Token(BaseModel):
    access_token: str
    token_type: str
    user_full_name: str 
class IssueBase(BaseModel):
    description: str
    department: str
    latitude: float
    longitude: float

class IssueCreate(IssueBase):
    pass

class Issue(IssueBase):
    id: int
    user_id: int
    photo_url: str
    audio_url: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True