# utils/cache.py
import redis
import json
import pickle
from functools import wraps
from typing import Optional, Any, Union
from datetime import timedelta
import os
from utils.logger import get_logger

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

logger = get_logger("cache")

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
                    logger.debug(f"Cache HIT for {cache_key}")
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache error (get): {e}")
                # If Redis is unavailable, continue without caching
                pass
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            try:
                redis_client.setex(cache_key, expire_time, json.dumps(result))
                logger.debug(f"Cache SET for {cache_key} (expires in {expire_time}s)")
            except Exception as e:
                logger.warning(f"Cache error (set): {e}")
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
        logger.debug(f"Cached user data for user {user_id}")
    except Exception as e:
        logger.warning(f"Failed to cache user data: {e}")

def get_cached_user_data(user_id: int) -> Optional[dict]:
    """Get cached user data."""
    cache_key = f"user:{user_id}:data"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.debug(f"Retrieved cached user data for user {user_id}")
            return json.loads(cached)
        return None
    except Exception as e:
        logger.warning(f"Failed to get cached user data: {e}")
        return None

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries related to a user."""
    try:
        pattern = f"*user:{user_id}*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries for user {user_id}")
    except Exception as e:
        logger.warning(f"Failed to invalidate user cache: {e}")

def cache_hoa_data(hoa_id: int, data: dict, expire_time: int = 1800):
    """Cache HOA-specific data."""
    cache_key = f"hoa:{hoa_id}:data"
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(data))
        logger.debug(f"Cached HOA data for HOA {hoa_id}")
    except Exception as e:
        logger.warning(f"Failed to cache HOA data: {e}")

def get_cached_hoa_data(hoa_id: int) -> Optional[dict]:
    """Get cached HOA data."""
    cache_key = f"hoa:{hoa_id}:data"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.debug(f"Retrieved cached HOA data for HOA {hoa_id}")
            return json.loads(cached)
        return None
    except Exception as e:
        logger.warning(f"Failed to get cached HOA data: {e}")
        return None

def invalidate_hoa_cache(hoa_id: int):
    """Invalidate all cache entries related to a HOA."""
    try:
        pattern = f"*hoa:{hoa_id}*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries for HOA {hoa_id}")
    except Exception as e:
        logger.warning(f"Failed to invalidate HOA cache: {e}")

def cache_violations_dashboard(user_id: int, hoa_id: Optional[int] = None, data: dict = None, expire_time: int = 300):
    """Cache dashboard violations data."""
    cache_key = f"dashboard:user:{user_id}:hoa:{hoa_id or 'all'}"
    try:
        if data is not None:
            redis_client.setex(cache_key, expire_time, json.dumps(data))
            logger.debug(f"Cached dashboard data for user {user_id}")
        else:
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug(f"Retrieved cached dashboard data for user {user_id}")
                return json.loads(cached)
        return None
    except Exception as e:
        logger.warning(f"Dashboard cache operation failed: {e}")
        return None

def cache_analytics_data(hoa_id: int, data: dict, expire_time: int = 1800):
    """Cache analytics data."""
    cache_key = f"analytics:hoa:{hoa_id}"
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(data))
        logger.debug(f"Cached analytics data for HOA {hoa_id}")
    except Exception as e:
        logger.warning(f"Failed to cache analytics data: {e}")

def get_cached_analytics_data(hoa_id: int) -> Optional[dict]:
    """Get cached analytics data."""
    cache_key = f"analytics:hoa:{hoa_id}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.debug(f"Retrieved cached analytics data for HOA {hoa_id}")
            return json.loads(cached)
        return None
    except Exception as e:
        logger.warning(f"Failed to get cached analytics data: {e}")
        return None

def warm_cache():
    """Pre-load frequently accessed data into cache."""
    try:
        from database import SessionLocal
        from models import HOA, User
        
        db = SessionLocal()
        
        # Warm up HOA data
        hoas = db.query(HOA).all()
        for hoa in hoas:
            hoa_data = {
                "id": hoa.id,
                "name": hoa.name,
                "location": hoa.location,
                "contact_email": hoa.contact_email,
                "contact_phone": hoa.contact_phone,
            }
            cache_hoa_data(hoa.id, hoa_data, expire_time=3600)
        
        # Warm up user data for active users
        active_users = db.query(User).filter(User.last_activity_at.isnot(None)).limit(100).all()
        for user in active_users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "hoa_id": user.hoa_id,
            }
            cache_user_data(user.id, user_data, expire_time=1800)
        
        db.close()
        logger.info(f"Cache warming completed: {len(hoas)} HOAs, {len(active_users)} users")
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")

def get_cache_stats() -> dict:
    """Get Redis cache statistics."""
    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
        }
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {}

def clear_all_cache():
    """Clear all cache entries (use with caution)."""
    try:
        redis_client.flushdb()
        logger.warning("All cache entries cleared")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}") 