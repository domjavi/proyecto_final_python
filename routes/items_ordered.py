from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlmodel import Session, select

from auth.dependencies import require_role
from db.database import get_session
from models.items_ordered import ItemsOrderedCreate, ItemsOrderedRead
from crud.items_ordered import(
    add_item_ordered,
    get_items_ordered,
    modify_item_quantity,
    delete_items_ordered
)
from models.order import Order

router = APIRouter()

@router.post("/items/add_item", response_model=ItemsOrderedRead)
async def add_item_to_order(
    item_data: ItemsOrderedCreate = Body(
        ...,
        examples={
            "example": {
                "summary": "An example item",
                "value": {
                    "item_id": 1,
                    "order_id": 1,
                    "quantity": 3,
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    order = session.exec(select(Order).where(Order.id == item_data.order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.owner_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this order")

    try:
        item = await add_item_ordered(
            session=session,
            product_id=item_data.item_id,
            order_id=item_data.order_id,
            quantity=item_data.quantity
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error adding item to order")

@router.get("/items/", response_model=list[ItemsOrderedRead])
def read_items(
    order_id: int = Query(..., description="Order ID to filter items by"),
    item_id: int = Query(None, description="Item ID to filter items by"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    try:
        if current_user["role"] == "client":
            order = session.exec(
                select(Order).where(Order.id == order_id, Order.owner_id == current_user["id"])
            ).first()
            if not order:
                raise HTTPException(status_code=403, detail="Not authorized to access this order")

        items = get_items_ordered(session, order_id=order_id, item_id=item_id, skip=skip, limit=limit)

        if not items:
            raise HTTPException(status_code=404, detail="No items found for this order")

        return items

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/items/{item_id}", response_model=ItemsOrderedRead)
def update_item_quantity(
    order_id: int = Query(..., description="ID del pedido al que pertenece el ítem"),
    item_id: int = Path(..., description="ID del ítem en el pedido"),
    new_quantity: int = Body(..., embed=True, ge=0, description="Nueva cantidad del ítem (0 para eliminar)"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user["role"] == "client" and order.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this order")

    try:
        if new_quantity == 0:
            deleted_item = delete_items_ordered(session, item_id=item_id, order_id=order_id)
            return deleted_item
        else:
            updated_item = modify_item_quantity(session, item_id=item_id, order_id=order_id, new_quantity=new_quantity)
            return updated_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/items/{item_id}", response_model=ItemsOrderedRead)
def delete_item_from_order(
    order_id: int = Query(..., description="Order ID to delete item from"),
    item_id: int = Path(..., description="Item ID to delete"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] == "client" and order.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete from this order")

    try:
        deleted_item = delete_items_ordered(session, item_id=item_id, order_id=order_id)
        return deleted_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
