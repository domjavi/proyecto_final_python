from fastapi import Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from auth.jwt import verify_access_token
from auth.hashing import verify_password
from sqlmodel import Session, select
from db.database import get_session
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload["sub"]
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }

def require_role(*allowed_roles: str):
    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency

def verify_current_password(current_password: str = Body(...), current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(User).where(User.username == current_user["username"])
    user = session.exec(statement).first()
    if not user or not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    return user
