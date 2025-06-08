import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from auth.redis_client import client_redis, revoke_token as redis_revoke_token


SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 1

REVOKED_TOKENS_KEY = "revoked_tokens"

# Archivo para almacenar tokens revocados
# REVOKED_TOKENS_FILE = "revoked_tokens.txt"

# # Cargar tokens revocados desde el archivo
# revoked_tokens = set()
# if os.path.exists(REVOKED_TOKENS_FILE):
#     with open(REVOKED_TOKENS_FILE, "r") as file:
#         revoked_tokens = set(line.strip() for line in file)

def create_access_token(data: dict, role: str, expires_minutes: int = None):
    to_encode = data.copy()
    if expires_minutes is None:
        role_expiration = {
            "admin": 60,  # 60 minutes
            "user": 30,  # 30 minutes
            "viewer": 15,  # 15 minutes
        }
        expires_minutes = role_expiration.get(role, ACCESS_TOKEN_EXPIRE_MINUTES)  # Default 15 minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "role": role})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        if is_token_revoked(token):  # Verificar si el token está revocado
            raise JWTError("Token has been revoked")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def revoke_token(token: str, expires_in: int = None):
    """
    Revocar un token y almacenarlo en Redis.
    Si no se indica `expires_in`, se calcula según el tiempo restante en el token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        if not expires_in and exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            expires_in = int((exp_time - datetime.now(timezone.utc)).total_seconds())
        if expires_in and expires_in > 0:
            redis_revoke_token(token, expires_in)
    except JWTError:
        redis_revoke_token(token, 900)  # 15 minutos de retención por defecto

def is_token_revoked(token: str) -> bool:
    """Verifica si un token ha sido revocado."""
    return client_redis.exists(f"REVOKED_TOKENS_KEY:{token}") == 1