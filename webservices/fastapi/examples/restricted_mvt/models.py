from typing import Optional
from sqlmodel import Field, SQLModel


class UsersReq(SQLModel):
    username: str
    password: str


class Users(UsersReq, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plz: Optional[str]
