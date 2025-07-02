# Performance and Caching Guide for A.I.ncident

## 🚀 Performance Optimization Strategies

### 1. Database Optimization

#### Query Optimization
- **Use eager loading** for related data to avoid N+1 queries
- **Implement pagination** for large datasets (already implemented)
- **Add database indexes** for frequently queried fields
- **Use database connection pooling** (already configured)

#### Recommended Database Indexes
```sql
-- Add these indexes to improve query performance
CREATE INDEX idx_incidents_store_name ON incidents(store_name);
CREATE INDEX idx_incidents_user_id ON incidents(user_id);
CREATE INDEX idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_store_id ON users(store_id);
```

### 2. Caching Strategy

#### Redis Caching Implementation
```python
# utils/cache.py
import redis
import json
from functools import wraps
from typing import Optional, Any

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expire_time: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage examples:
@cache_result(expire_time=600)  # Cache for 10 minutes
def get_store_info(store_id: int) -> dict:
    """Get store information with caching."""
    # Database query here
    pass

@cache_result(expire_time=300)  # Cache for 5 minutes
def get_user_permissions(user_id: int) -> list:
    """Get user permissions with caching."""
    # Database query here
    pass
```

#### Cache Invalidation Strategy
```python
def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries related to a user."""
    pattern = f"*user_id:{user_id}*"
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

def invalidate_store_cache(store_id: int):
    """Invalidate all cache entries related to a store."""
    pattern = f"*store_id:{store_id}*"
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
```

### 3. File Storage Optimization

#### Image Processing
```python
# utils/image_processor.py
from PIL import Image
import io

def optimize_image(image_data: bytes, max_size: tuple = (800, 600)) -> bytes:
    """Optimize image for web display."""
    img = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA'):
        img = img.convert('RGB')
    
    # Resize if too large
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save with optimization
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    return output.getvalue()
```

#### PDF Generation Optimization
```python
# utils/pdf_optimizer.py
def optimize_pdf_generation(incident_data: dict) -> str:
    """Optimize PDF generation with caching."""
    cache_key = f"pdf:{incident_data['id']}"
    
    # Check if PDF already exists
    cached_pdf = redis_client.get(cache_key)
    if cached_pdf:
        return cached_pdf
    
    # Generate PDF
    pdf_path = generate_pdf(incident_data)
    
    # Cache the path
    redis_client.setex(cache_key, 3600, pdf_path)  # Cache for 1 hour
    return pdf_path
```

### 4. API Response Optimization

#### Response Compression
```python
# main.py - Add compression middleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### Response Caching Headers
```python
# Add to your route handlers
from fastapi.responses import Response

@router.get("/incidents/")
def get_incidents(...):
    # ... your logic ...
    
    response = Response(content=json.dumps(data))
    response.headers["Cache-Control"] = "public, max-age=300"  # Cache for 5 minutes
    return response
```

### 5. Background Task Processing

#### Celery Integration for Heavy Tasks
```python
# tasks.py
from celery import Celery

celery_app = Celery('incidentiq', broker='redis://localhost:6379/1')

@celery_app.task
def process_incident_async(incident_id: int):
    """Process incident asynchronously."""
    # Heavy processing like AI analysis, email notifications, etc.
    pass

@celery_app.task
def generate_pdf_async(incident_id: int):
    """Generate PDF asynchronously."""
    # PDF generation
    pass

# Usage in your routes:
@router.post("/incidents/")
def create_incident(...):
    # ... create incident ...
    
    # Trigger async tasks
    process_incident_async.delay(incident.id)
    generate_pdf_async.delay(incident.id)
    
    return incident
```

### 6. Monitoring and Metrics

#### Performance Monitoring
```python
# utils/monitoring.py
import time
from functools import wraps

def monitor_performance(func_name: str = None):
    """Decorator to monitor function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"Performance: {func_name or func.__name__} took {duration:.3f}s")
            
            # Alert if too slow
            if duration > 5.0:  # 5 seconds threshold
                logger.warning(f"Slow operation: {func_name or func.__name__} took {duration:.3f}s")
            
            return result
        return wrapper
    return decorator
```

### 7. Configuration for Production

#### Environment Variables
```bash
# .env.production
REDIS_URL=redis://your-redis-server:6379
DATABASE_URL=postgresql://user:pass@host:port/db
WORKERS=4
MAX_CONNECTIONS=100
CACHE_TTL=300
```

#### Docker Configuration
```dockerfile
# Dockerfile.optimized
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with multiple workers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8. Performance Testing

#### Load Testing Script
```python
# tests/load_test.py
import asyncio
import aiohttp
import time

async def load_test():
    """Simple load test for the API."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):  # 100 concurrent requests
            task = session.get('http://localhost:8000/api/incidents/')
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        successful = sum(1 for r in responses if r.status == 200)
        print(f"Load test completed: {successful}/100 successful in {end_time - start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(load_test())
```

## 📊 Performance Benchmarks

### Current Performance Targets
- **API Response Time**: < 200ms for most endpoints
- **Database Queries**: < 50ms for simple queries
- **File Upload**: < 2s for 10MB files
- **PDF Generation**: < 5s for complex reports
- **Concurrent Users**: 100+ simultaneous users

### Monitoring Tools
- **Application Metrics**: Custom logging and timing
- **Database Performance**: PostgreSQL query analysis
- **System Resources**: CPU, memory, disk I/O monitoring
- **External Services**: Stripe API response times

## 🔧 Implementation Priority

### High Priority (Implement First)
1. Database indexes for frequently queried fields
2. Response compression middleware
3. Basic caching for store and user data
4. Image optimization for uploads

### Medium Priority
1. Redis caching implementation
2. Background task processing
3. Performance monitoring
4. PDF generation optimization

### Low Priority (Future Enhancements)
1. CDN integration for static files
2. Advanced caching strategies
3. Microservices architecture
4. Advanced monitoring and alerting

## 📝 Notes

- Monitor Redis memory usage and implement eviction policies
- Set up automated performance testing in CI/CD pipeline
- Implement circuit breakers for external API calls
- Consider using connection pooling for database connections
- Implement rate limiting for API endpoints (already partially implemented) 