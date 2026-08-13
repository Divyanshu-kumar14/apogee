"""
Simple in-memory caching utilities for expensive operations.
Uses functools.lru_cache with time-based expiration.
"""
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def timed_lru_cache(seconds: int = 3600, maxsize: int = 128):
    """
    LRU cache decorator with time-based expiration.
    
    Args:
        seconds: Cache TTL in seconds (default: 1 hour)
        maxsize: Maximum cache size (default: 128)
    
    Returns:
        Decorated function with timed cache
    
    Example:
        @timed_lru_cache(seconds=3600)
        def expensive_function(arg):
            return compute_result(arg)
    """
    def decorator(func: Callable) -> Callable:
        # Create cache key that includes timestamp bucket
        @lru_cache(maxsize=maxsize)
        def cached_func_with_time(time_bucket, *args, **kwargs):
            return func(*args, **kwargs)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create time bucket (rounds down to nearest interval)
            now = datetime.utcnow()
            time_bucket = int(now.timestamp() // seconds)
            
            # Call cached function with time bucket
            return cached_func_with_time(time_bucket, *args, **kwargs)
        
        # Add cache info and clear methods
        wrapper.cache_info = cached_func_with_time.cache_info
        wrapper.cache_clear = cached_func_with_time.cache_clear
        
        return wrapper
    
    return decorator


# Pre-configured cache decorators for common use cases

def cache_tle_data(func: Callable) -> Callable:
    """
    Cache TLE data for 1 hour.
    TLE data doesn't change frequently, so 1 hour is reasonable.
    """
    return timed_lru_cache(seconds=3600, maxsize=256)(func)


def cache_tess_query(func: Callable) -> Callable:
    """
    Cache TESS query results for 24 hours.
    TESS data is static, so long cache is appropriate.
    """
    return timed_lru_cache(seconds=86400, maxsize=128)(func)


def cache_orbital_calculation(func: Callable) -> Callable:
    """
    Cache orbital calculations for 5 minutes.
    Orbital positions change frequently, so shorter cache.
    """
    return timed_lru_cache(seconds=300, maxsize=512)(func)


def cache_api_response(func: Callable) -> Callable:
    """
    Cache API responses for 5 minutes.
    General purpose API response caching.
    """
    return timed_lru_cache(seconds=300, maxsize=256)(func)
