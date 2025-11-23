from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pair import Pair
    from app.models.event import Event

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_token: Optional[str] = Field(default=None)
    password: str
    pair_id: Optional[int] = Field(default=None, foreign_key="pair.id")
    pair: Optional["Pair"] = Relationship(back_populates="users")
    events: List["Event"] = Relationship(back_populates="user")
 
class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    pair_id: Optional[int]
