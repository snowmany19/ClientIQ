# utils/cache.py
import redis
import json
import pickle
from functools import wraps
from typing import Optional, Any, Union
from datetime import timedelta
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def cache_result(expire_time: int = 300, key_prefix: str = ""):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            try:
                # Try to get from cache
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            except Exception as e:
                # If Redis is unavailable, continue without caching
                pass
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            try:
                redis_client.setex(cache_key, expire_time, json.dumps(result))
            except Exception as e:
                # If Redis is unavailable, continue without caching
                pass
                
            return result
        return wrapper
    return decorator

def cache_user_data(user_id: int, data: dict, expire_time: int = 600):
    """Cache user-specific data."""
    cache_key = f"user:{user_id}:data"
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(data))
    except Exception:
        pass

def get_cached_user_data(user_id: int) -> Optional[dict]:
    """Get cached user data."""
    cache_key = f"user:{user_id}:data"
    try:
        cached = redis_client.get(cache_key)
        return json.loads(cached) if cached else None
    except Exception:
        return None

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries related to a user."""
    try:
        pattern = f"user:{user_id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass

def cache_hoa_data(hoa_id: int, data: dict, expire_time: int = 1800):
    """Cache HOA-specific data."""
    cache_key = f"hoa:{hoa_id}:data"
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(data))
    except Exception:
        pass

def get_cached_hoa_data(hoa_id: int) -> Optional[dict]:
    """Get cached HOA data."""
    cache_key = f"hoa:{hoa_id}:data"
    try:
        cached = redis_client.get(cache_key)
        return json.loads(cached) if cached else None
    except Exception:
        return None

def invalidate_hoa_cache(hoa_id: int):
    """Invalidate all cache entries related to a HOA."""
    try:
        pattern = f"hoa:{hoa_id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass

def cache_violations_list(cache_key: str, violations: list, expire_time: int = 300):
    """Cache violations list."""
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(violations))
    except Exception:
        pass

def get_cached_violations_list(cache_key: str) -> Optional[list]:
    """Get cached violations list."""
    try:
        cached = redis_client.get(cache_key)
        return json.loads(cached) if cached else None
    except Exception:
        return None

def clear_all_cache():
    """Clear all cache (use with caution)."""
    try:
        redis_client.flushdb()
    except Exception:
        pass

def get_cache_stats() -> dict:
    """Get cache statistics."""
    try:
        info = redis_client.info()
        return {
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
    except Exception:
        return {"error": "Unable to get cache stats"} 