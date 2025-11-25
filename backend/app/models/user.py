from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models.link import UserPairLink
from app.models.event import Event
from app.models.pair import Pair

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_token: Optional[str] = Field(default=None)
    password: str
    pairs: List["Pair"] = Relationship(
        back_populates="users",
        link_model=UserPairLink
    )
    events: List["Event"] = Relationship(back_populates="user")
 
class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserRead(UserBase):
    id: int
