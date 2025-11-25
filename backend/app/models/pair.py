from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

from app.models.link import UserPairLink

class PairBase(SQLModel):
    name: str
    code: str = Field(unique=True, index=True, default="")

class Pair(PairBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    users: List["User"] = Relationship(
        back_populates="pairs",
        link_model=UserPairLink
    )

class PairCreate(PairBase):
    pass

class PairRead(PairBase):
    id: int