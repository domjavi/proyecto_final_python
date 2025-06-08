from sqlmodel import Session, select
from models.items_ordered import ItemsOrdered
from models.order import Order
import httpx


url = "https://dummyjson.com/products"

async def add_item_ordered(session: Session, product_id: int, order_id: int, quantity: int):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{url}/{product_id}")
        if response.status_code != 200:
            raise ValueError(f"Product with id {product_id} not found in API.")
        product = response.json()
    
    existing_item = session.exec(
        select(ItemsOrdered).where(
            ItemsOrdered.item_id == product["id"],
            ItemsOrdered.order_id == order_id
        )
    ).first()
    if existing_item:
        existing_item.quantity += quantity
        session.commit()
        session.refresh(existing_item)
        return existing_item

    item = ItemsOrdered(
        item_id=product["id"],
        title=product["title"],
        description=product.get("description", ""),
        category=product.get("category", ""),
        price=product.get("price", 0.0),
        rating=product.get("rating", 0.0),
        brand=product.get("brand", ""),
        order_id=order_id,
        quantity=quantity
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def get_items_ordered(session: Session, order_id: int = None, user_id: int = None, item_id: int = None, skip: int = 0, limit: int = 100):
    statement = select(ItemsOrdered)
    if order_id is not None:
        statement = statement.where(ItemsOrdered.order_id == order_id)
    elif user_id is not None:
        user_orders = session.exec(select(Order.id).where(Order.owner_id == user_id)).all()
        if not user_orders:
            raise ValueError(f"No orders found for user with id {user_id}.")
        statement = statement.where(ItemsOrdered.order_id.in_(user_orders))

    if item_id is not None:
        statement = statement.where(ItemsOrdered.item_id == item_id)

    statement = statement.offset(skip).limit(limit)
    items = session.exec(statement).all()
    return items

def modify_item_quantity(session: Session, item_id: int, order_id: int, new_quantity: int):
    order = session.get(Order, order_id)
    if not order:
        raise ValueError(f"Order with id {order_id} not found.")

    item = session.exec(
        select(ItemsOrdered).where(
        ItemsOrdered.item_id == item_id,
        ItemsOrdered.order_id == order_id
        )
    ).first()
    if not item:
        raise ValueError(f"Item with id {item_id} not found in order {order_id}.")

    item.quantity = new_quantity
    session.commit()
    session.refresh(item)
    return item

def delete_items_ordered(session: Session, item_id: int, order_id: int):
    item = session.exec(
        select(ItemsOrdered).where(
            ItemsOrdered.item_id == item_id,
            ItemsOrdered.order_id == order_id
        )
    ).first()
    if not item:
        raise ValueError(f"Item with id {item_id} not found in order {order_id}.")
    session.delete(item)
    session.commit()
    return item