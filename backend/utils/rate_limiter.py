# backend/utils/rate_limiter.py

from fastapi import Request, HTTPException, status
from typing import Optional
import time
from collections import defaultdict, deque


class RateLimiter:
    """Custom rate limiter for production use."""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed for the given IP."""
        now = time.time()
        window_start = now - 60  # 1 minute window
        
        # Clean old requests
        if client_ip in self.requests:
            while self.requests[client_ip] and self.requests[client_ip][0] < window_start:
                self.requests[client_ip].popleft()
        
        # Check if under limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for the given IP."""
        now = time.time()
        window_start = now - 60
        
        if client_ip in self.requests:
            # Clean old requests
            while self.requests[client_ip] and self.requests[client_ip][0] < window_start:
                self.requests[client_ip].popleft()
            
            return max(0, self.requests_per_minute - len(self.requests[client_ip]))
        
        return self.requests_per_minute


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded headers (for proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


def rate_limit_middleware(rate_limiter: RateLimiter):
    """Middleware function for rate limiting."""
    async def middleware(request: Request, call_next):
        client_ip = get_client_ip(request)
        
        if not rate_limiter.is_allowed(client_ip):
            remaining = rate_limiter.get_remaining_requests(client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in 60 seconds. Remaining requests: {remaining}"
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = rate_limiter.get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
        
        return response
    
    return middleware 