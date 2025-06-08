from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import redis_client
from auth.jwt import(
    create_access_token, create_refresh_token,
    verify_refresh_token, revoke_token, verify_access_token, is_token_revoked
)
from auth.hashing import hash_password, verify_password, validate_password_strength
from db.database import get_session
from auth.dependencies import get_current_user, oauth2_scheme, verify_current_password, require_role
from models.user import User, UserCreate, UserRead
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    try:
        validate_password_strength(user.password)  # Validate password strength
        statement = select(User).where(User.username == user.username)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = hash_password(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role  # Default role is "client"
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username}, role=user.role)
    refresh_token = create_refresh_token({"sub": user.username})
    user.refresh_token = refresh_token
    session.add(user)
    session.commit()
    logger.info(f"User {user.username} logged in successfully")
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str, session: Session = Depends(get_session)):
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    statement = select(User).where(User.refresh_token == refresh_token)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access_token = create_access_token({"sub": user.username}, role=user.role)
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    statement = select(User).where(User.username == current_user["username"])
    user = session.exec(statement).first()
    if not user:
        logger.warning(f"Logout attempt for non-existent user: {current_user['username']}")
        raise HTTPException(status_code=404, detail="User not found")
    user.refresh_token = None
    session.add(user)
    session.commit()
    revoke_token(token)
    logger.info(f"User {user.username} logged out successfully")
    return {"message": "Successfully logged out"}

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_view(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
def forgot_password(email: str = Form(...), session: Session = Depends(get_session)):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    token = create_access_token({"sub": user.email}, role="reset", expires_minutes=15)
    logger.info(f"Password reset token generated for email: {email}")
    return {"message": "Use this token to reset your password", "token": token}

@router.post("/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), session: Session = Depends(get_session)):
    payload = verify_access_token(token)
    if not payload or payload.get("role") != "reset":
        logger.warning("Invalid or expired password reset token used")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    email = payload.get("sub")
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        logger.warning(f"Password reset attempt for non-existent email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    logger.info(f"Password reset successfully for email: {user.email}")
    return RedirectResponse(url="/", status_code=303)

@router.post("/change-password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    user: User = Depends(verify_current_password),
    session: Session = Depends(get_session),
):
    if current_password == new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current password")
    
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    return {"message": "Password updated successfully"}

@router.get("/revoked-tokens", response_model=list[str])
def list_revoked_tokens(current_user: dict = Depends(require_role("admin"))):
    keys = redis_client.keys("REVOKED_TOKENS_KEY:*")
    return [key.split(":")[1] for key in keys if redis_client.exists(key)]

@router.post("/revoke-token")
def revoke_token_endpoint(token: str = Form(...), current_user: dict = Depends(require_role("admin"))):
    if is_token_revoked(token):
        raise HTTPException(status_code=400, detail="Token is already revoked")
    revoke_token(token)
    return {"message": "Token revoked successfully"}
