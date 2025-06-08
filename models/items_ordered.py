from sqlmodel import SQLModel, Field
from typing import Optional

class ItemsOrderedBase(SQLModel):
    item_id: int = Field(index=True, nullable=False)
    order_id: int = Field(nullable=False, foreign_key="order.id", ondelete="CASCADE")
    quantity: int = Field(default=1, ge=1)

class ItemsOrdered(ItemsOrderedBase, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    category: str = Field(nullable=False)
    price: float = Field(default=0.0)
    rating: float = Field(default=0.0)
    brand: str = Field(nullable=False)

class ItemsOrderedCreate(ItemsOrderedBase):
    pass
class ItemsOrderedRead(ItemsOrderedBase):
    title: str
    description: Optional[str]
    category: str
    price: float
    rating: float
    brand: str