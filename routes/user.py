from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import Session

from auth.dependencies import require_role
from db.database import get_session
from models.user import UserCreate, UserRead
from crud.user import(
    create_user,
    delete_user,
    get_users,
    update_user
)


router = APIRouter()

@router.post("/users/", response_model=UserRead)
def create(
    user_data: UserCreate = Body(
        ...,
        examples={
            "example": {
                "summary": "An example user",
                "value": {
                    "username": "exampleuser",
                    "email": "user@example.com",
                    "password": "examplepassword",
                    "role": "user"  # Default role is "user"
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin"))
):
    try:
        created_user = create_user(session, user_data.username, user_data.email, user_data.password, user_data.role)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/", response_model=list[UserRead])
def read(
    id: int = Query(None, description="ID del usuario"),
    username: str = Query(None, description="Nombre de usuario"),
    email: str = Query(None, description="Correo electrónico"),
    skip: int = Query(0, description="Número de usuarios a omitir"),
    limit: int = Query(100, description="Número máximo de usuarios a devolver"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "client":
        users = get_users(session, id=current_user["id"])
    else:    
        users = get_users(session, id=id, username=username, email=email, skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@router.put("/users/{user_id}", response_model=UserRead)
def update(
    user_id: int,
    user_data: UserCreate = Body(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if (current_user["role"] == "client") and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own user data")
    updated_user = update_user(session, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}", response_model=UserRead)
def delete(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin", "client"))
):
    if current_user["role"] == "client":
        user_id = current_user["id"]
    deleted_user = delete_user(session, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
