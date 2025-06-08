from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import Session

from auth.dependencies import require_role
from db.database import get_session
from models.order import Order, OrderCreate, OrderRead
from crud.user import get_users
from crud.order import (
    create_order,
    delete_order,
    get_orders,
)

router = APIRouter()

@router.post("/orders/", response_model=OrderRead)
def create(
    order: OrderCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin", "client"))
):
    try:
        if current_user["role"] == "admin":
            owner_id = order.owner_id
        elif current_user["role"] == "client":
            owner_id = current_user["id"]
        else:
            raise HTTPException(status_code=403, detail="Insufficient permissions to create an order")
        owner = get_users(session, id=owner_id)
        if not owner:
            raise HTTPException(status_code=404, detail="User not found")
        if isinstance(owner, list):
            owner = owner[0]
        order_data = order.model_dump(exclude={"id", "created_at"})
        order_data["owner_id"] = owner.id
        created_order = create_order(session, **order_data)
        session.refresh(created_order)
        return created_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/", response_model=list[OrderRead])
def read(
    order_id: int = Query(None, description="Order ID"),
    owner_id: int = Query(None, description="Order owner ID"),
    username: str = Query(None, description="Order owner username"),
    email: str = Query(None, description="Order owner email"),
    skip: int = Query(0, description="Number of orders to skip"),
    limit: int = Query(100, description="Maximum number of orders to return"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "admin":
        owner_id = owner_id
    if current_user["role"] == "client":
        owner_id = current_user["id"]
    orders = get_orders(session, order_id=order_id, owner_id=owner_id, username=username, email=email, skip=skip, limit=limit)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

@router.put("/orders/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    order_data: OrderCreate = Body(
        ...,
        examples={
            "example": {
                "summary": "Update order owner (admin only)",
                "value": {
                    "owner_id": 1
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    existing_order = session.get(Order, order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user["role"] == "admin":
        owner_id = order_data.owner_id
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update an order")
    
    order_data_dict = order_data.model_dump()
    updated_order = update_order(session, order_id, order_data_dict)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@router.delete("/orders/{order_id}", response_model=OrderRead)
def delete(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    existing_order = session.get(Order, order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] == "admin":
        owner_id = existing_order.owner_id
    elif current_user["role"] == "client":
        owner_id = current_user["id"]
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete an order")
    deleted_order = delete_order(session, order_id)
    if not deleted_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return deleted_order
