from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from sqlalchemy import text
from typing import Optional

class UserAuthModel(SQLModel, table=True):
    __tablename__ = "authtable"

    id : int | None = Field(default=None, primary_key=True)
    username : str
    email : str
    password : str
    role : str = Field(default="USER")
    is_verified : bool = Field(default=False, sa_column_kwargs={"server_default": text("false")})
    created_at : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

class CreateUserModel(SQLModel):
    username : str
    email : str
    password : str
    role : str | None = None

class LoginUserModel(SQLModel):
    email : str
    password : str

class EmailModel(SQLModel):
    emailaddress : list[str]

class UpdateModel(SQLModel):
    username : Optional[str] = None
    email : Optional[str] = None
    password : Optional[str] = None
    is_verified : Optional[bool] = False