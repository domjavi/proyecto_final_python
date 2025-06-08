import os
import redis
from datetime import timedelta

# Conexión a Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
client_redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def revoke_token(token: str, expiration: int):
    """Revoca un token almacenándolo en Redis con un tiempo de expiración."""
    client_redis.setex(token, timedelta(seconds=expiration), "revoked")

def is_token_revoked(token: str) -> bool:
    """Verifica si un token ha sido revocado."""
    return client_redis.exists(token) == 1