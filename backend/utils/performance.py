# utils/performance.py
import time
import functools
from typing import Callable, Any
from utils.logger import get_logger

logger = get_logger("performance")

def monitor_performance(func_name: str = None, threshold: float = 1.0):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance metrics
                logger.info(
                    f"Performance: {func_name or func.__name__} completed in {duration:.3f}s",
                    extra={
                        "function": func_name or func.__name__,
                        "duration": duration,
                        "status": "success"
                    }
                )
                
                # Alert if too slow
                if duration > threshold:
                    logger.warning(
                        f"Slow operation: {func_name or func.__name__} took {duration:.3f}s (threshold: {threshold}s)",
                        extra={
                            "function": func_name or func.__name__,
                            "duration": duration,
                            "threshold": threshold,
                            "status": "slow"
                        }
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Performance: {func_name or func.__name__} failed after {duration:.3f}s: {str(e)}",
                    extra={
                        "function": func_name or func.__name__,
                        "duration": duration,
                        "error": str(e),
                        "status": "error"
                    }
                )
                raise
        
        return wrapper
    return decorator

def monitor_api_performance(threshold: float = 2.0):
    """Decorator specifically for API endpoint performance monitoring."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log API performance
                logger.info(
                    f"API Performance: {func.__name__} completed in {duration:.3f}s",
                    extra={
                        "endpoint": func.__name__,
                        "duration": duration,
                        "status": "success"
                    }
                )
                
                # Alert if too slow
                if duration > threshold:
                    logger.warning(
                        f"Slow API endpoint: {func.__name__} took {duration:.3f}s (threshold: {threshold}s)",
                        extra={
                            "endpoint": func.__name__,
                            "duration": duration,
                            "threshold": threshold,
                            "status": "slow"
                        }
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"API Performance: {func.__name__} failed after {duration:.3f}s: {str(e)}",
                    extra={
                        "endpoint": func.__name__,
                        "duration": duration,
                        "error": str(e),
                        "status": "error"
                    }
                )
                raise
        
        return wrapper
    return decorator

class PerformanceTracker:
    """Context manager for tracking performance of code blocks."""
    
    def __init__(self, operation_name: str, threshold: float = 1.0):
        self.operation_name = operation_name
        self.threshold = threshold
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.info(
                f"Performance: {self.operation_name} completed in {duration:.3f}s",
                extra={
                    "operation": self.operation_name,
                    "duration": duration,
                    "status": "success"
                }
            )
            
            if duration > self.threshold:
                logger.warning(
                    f"Slow operation: {self.operation_name} took {duration:.3f}s (threshold: {self.threshold}s)",
                    extra={
                        "operation": self.operation_name,
                        "duration": duration,
                        "threshold": self.threshold,
                        "status": "slow"
                    }
                )
        else:
            logger.error(
                f"Performance: {self.operation_name} failed after {duration:.3f}s: {str(exc_val)}",
                extra={
                    "operation": self.operation_name,
                    "duration": duration,
                    "error": str(exc_val),
                    "status": "error"
                }
            )

def track_database_query(query_name: str = None):
    """Decorator for tracking database query performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with PerformanceTracker(f"DB Query: {query_name or func.__name__}", threshold=0.5):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage examples:
# @monitor_performance("get_violations", threshold=1.0)
# def get_violations():
#     pass

# @monitor_api_performance(threshold=2.0)
# async def api_endpoint():
#     pass

# with PerformanceTracker("complex_operation", threshold=5.0):
#     # complex operation here
#     pass 