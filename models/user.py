from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Models
class UserBase(SQLModel):
    username: str = Field(nullable=False, index=True, unique=True)
    email: EmailStr = Field(nullable=False, index=True, unique=True)
    role: str = Field(default="client")
    
class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    refresh_token: str = Field(default=None, nullable=True)

class UserCreate(UserBase):
    password: str = Field(nullable=False)

class UserRead(UserBase):
    pass