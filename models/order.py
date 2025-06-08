import datetime
from sqlmodel import SQLModel, Field

class OrderBase(SQLModel):
    owner_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE")

class Order(OrderBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class OrderCreate(OrderBase):
    pass

class OrderRead(OrderBase):
    id: int
    created_at: datetime.datetime