# backend/main.py

import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest

# 👇 Fix path issues for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from core.config import get_settings
from utils.logger import setup_logging, get_logger, log_api_request, log_error
from utils.rate_limiter import RateLimiter, rate_limit_middleware, get_client_ip
from utils.exceptions import custom_exception_handler, CivicLogHOAException
from utils.cache import warm_cache, get_cache_stats

# Get settings
settings = get_settings()

# Setup logging
logger = setup_logging(settings.log_level)

# Initialize rate limiter
rate_limiter = RateLimiter(settings.rate_limit_requests)

# Prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CivicLogHOA - HOA Violation Management Platform backend...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create static directories
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Warm up cache on startup
    try:
        logger.info("Warming up cache...")
        warm_cache()
        logger.info("Cache warming completed")
    except Exception as e:
        logger.warning(f"Cache warming failed: {e}")
    
    logger.info("CivicLogHOA - HOA Violation Management Platform backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CivicLogHOA - HOA Violation Management Platform backend...")

# ✅ FastAPI app with lifespan
app = FastAPI(
    title="CivicLogHOA - HOA Violation Management Platform API",
    description="Production-ready HOA violation management API",
    version="1.0.0",
    lifespan=lifespan
)

# 🔌 Include routers
from routes import auth, violations, billing, resident_portal, analytics, communications, settings as user_settings

app.include_router(auth.router, prefix="/api")
app.include_router(violations.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(resident_portal.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(communications.router, prefix="/api")
app.include_router(user_settings.router, prefix="/api")

# Debug router removed

# 🔒 Security Middleware
if settings.environment == "production":
    # Trusted hosts middleware for production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domain in production
    )

# 🚦 Rate Limiting Middleware
app.middleware("http")(rate_limit_middleware(rate_limiter))

# 🌐 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 🗜️ GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# �� Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🚨 Add custom exception handler
app.add_exception_handler(Exception, custom_exception_handler)

# 📊 Request Logging Middleware with Prometheus metrics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    log_api_request(
        logger,
        method=request.method,
        path=str(request.url.path),
        status_code=0,  # Will be updated after response
        user_id=None,  # Will be extracted if authenticated
        duration=None  # Will be calculated after response
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Update metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Update logging with final values
    log_api_request(
        logger,
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        user_id=None,  # Could extract from JWT if needed
        duration=duration
    )
    
    return response

# 🏥 Health Check Endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check for production monitoring."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
        "services": {}
    }
    
    # Check database connection
    try:
        from database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connection (if configured)
    try:
        from utils.cache import redis_client
        if hasattr(redis_client, 'ping'):
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_configured"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check external services
    try:
        if settings.openai_api_key:
            health_status["services"]["openai"] = "configured"
        else:
            health_status["services"]["openai"] = "not_configured"
    except:
        health_status["services"]["openai"] = "not_configured"
    
    try:
        if settings.stripe_secret_key:
            health_status["services"]["stripe"] = "configured"
        else:
            health_status["services"]["stripe"] = "not_configured"
    except:
        health_status["services"]["stripe"] = "not_configured"
    
    # Check SMTP configuration
    try:
        if settings.smtp_username and settings.smtp_password:
            health_status["services"]["smtp"] = "configured"
        else:
            health_status["services"]["smtp"] = "not_configured"
    except:
        health_status["services"]["smtp"] = "not_configured"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(
        content=health_status,
        status_code=status_code,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# 📊 Metrics Endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# 🔄 Cache management endpoints
@app.post("/api/cache/warm")
async def warm_cache_endpoint():
    """Manually trigger cache warming."""
    try:
        warm_cache()
        return {"status": "success", "message": "Cache warming completed"}
    except Exception as e:
        logger.error(f"Manual cache warming failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/cache/stats")
async def cache_stats_endpoint():
    """Get cache statistics."""
    try:
        stats = get_cache_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"status": "error", "message": str(e)}

# 🔍 Schema verification on startup
@app.on_event("startup")
async def verify_schemas():
    """Verify that all schemas are properly loaded."""
    try:
        from schemas import UserInfo
        # Check if UserInfo schema has required fields
        if hasattr(UserInfo, 'id'):
            logger.info("UserInfo schema loaded correctly with 'id' field")
        else:
            logger.warning("UserInfo schema missing 'id' field")
    except Exception as e:
        logger.warning(f"Could not verify UserInfo schema: {e}")

# 🚀 Startup delay for development (disabled for better performance)
# if settings.environment == "development":
#     import asyncio
#     asyncio.create_task(asyncio.sleep(1))  # Small delay for development


