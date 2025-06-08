from sqlmodel import Session, select
from models.order import Order
from models.user import User

def create_order(session: Session, owner_id: int):
    order = Order(owner_id=owner_id)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def get_orders(session: Session, order_id: int | None = None, owner_id: int | None = None, username: str | None = None, email: str | None = None, skip: int = 0, limit: int = 100):
    if order_id is not None:
        order = session.get(Order, order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} does not exist.")
        return [order]

    user_ids = []
    if username is not None or email is not None:
        user_statement = select(User.id)
        if username is not None:
            user_statement = user_statement.where(User.username == username)
        if email is not None:
            user_statement = user_statement.where(User.email == email)
        user_ids = session.exec(user_statement).all()
        if not user_ids:
            raise ValueError("No user found with the provided username or email.")
    elif owner_id is not None:
        user = session.get(User, owner_id)
        if not user:
            raise ValueError(f"No user found with id {owner_id}.")
        user_ids = [owner_id]

    if user_ids:
        statement = select(Order).where(Order.owner_id.in_(user_ids))
    else:
        statement = select(Order)

    statement = statement.offset(skip).limit(limit)
    orders = session.exec(statement).all()

    if (owner_id is not None or username is not None or email is not None) and not orders:
        raise ValueError("No orders found for the specified user.")

    return orders

def update_order(session: Session, order_id: int, order_data: dict):
    existing_order = session.get(Order, order_id)
    if not existing_order:
        return None
    for key, value in order_data.items():
        setattr(existing_order, key, value)
    session.commit()
    session.refresh(existing_order)
    return existing_order

def delete_order(session: Session, order_id: int):
    existing_order = session.get(Order, order_id)
    if not existing_order:
        raise ValueError(f"Order with id {order_id} does not exist.")
    session.delete(existing_order)
    session.commit()
    return existing_order
