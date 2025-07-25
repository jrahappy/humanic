"""Redis connection pool for chat application."""
import os
import environ
from pathlib import Path
from redis import Redis, ConnectionPool
from django.conf import settings

# Initialize environment
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Create a singleton connection pool
_redis_pool = None


def get_redis_pool():
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        # Build Redis URL securely
        redis_host = env('REDIS_URL', default='localhost')
        redis_password = env('REDIS_PASSWORD', default='')
        redis_port = env('REDIS_PORT', default=6379)
        redis_db = env('REDIS_DB', default=0)
        
        # Create connection pool
        _redis_pool = ConnectionPool(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            decode_responses=True,
            max_connections=50
        )
    return _redis_pool


def get_redis_connection():
    """Get a Redis connection from the pool."""
    pool = get_redis_pool()
    return Redis(connection_pool=pool)