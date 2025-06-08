from pydantic import EmailStr
from sqlmodel import Session, select
from auth.hashing import hash_password
from models.user import User, UserCreate

def create_user(session: Session, username: str, email: EmailStr, password: str, role: str = "client"):
    existing_user = session.exec(
        select(User).where(
            (User.username == username) | (User.email == email)
        )
    ).first()
    if existing_user:
        raise ValueError(f"A user with username '{username}' or email '{email}' already exists.")
    hashed_password = hash_password(password)
    user_data = User(username=username, email=email, hashed_password=hashed_password, role=role)
    if not user_data.username or not user_data.email or not user_data.hashed_password:
        raise ValueError("Username, email, and password are required fields.")
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data

def get_users(session: Session, id: int = None, username: str = None, email: str = None, skip: int = 0, limit: int = 100):
    statement = select(User)
    if id is not None:
        statement = statement.where(User.id == id)
    if username is not None:
        statement = statement.where(User.username == username)
    if email is not None:
        statement = statement.where(User.email == email)
    statement = statement.offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users

def update_user(session: Session, user_id: int, user_data: UserCreate):
    existing_user = session.get(User, user_id)
    if not existing_user:
        return None
    for key, value in user_data.model_dump(exclude={"id", "password"}).items():
        setattr(existing_user, key, value)
    if user_data.password:
        existing_user.hashed_password = hash_password(user_data.password)
    session.commit()
    session.refresh(existing_user)
    return existing_user

def delete_user(session: Session, user_id: int):
    existing_user = session.get(User, user_id)
    if not existing_user:
        return None
    session.delete(existing_user)
    session.commit()
    return existing_user