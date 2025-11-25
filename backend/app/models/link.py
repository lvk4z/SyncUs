from typing import Optional
from sqlmodel import SQLModel, Field

class UserPairLink(SQLModel, table=True):
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    pair_id: Optional[int] = Field(
        default=None, foreign_key="pair.id", primary_key=True
    )