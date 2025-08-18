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
from utils.exceptions import custom_exception_handler, ContractGuardAIException
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
    logger.info("Starting ContractGuard.ai - AI Contract Review Platform backend...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create static directories
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("static/documents", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Warm up cache on startup
    try:
        logger.info("Warming up cache...")
        warm_cache()
        logger.info("Cache warming completed")
    except Exception as e:
        logger.warning(f"Cache warming failed: {e}")
    
    logger.info("ContractGuard.ai - AI Contract Review Platform backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ContractGuard.ai - AI Contract Review Platform backend...")

# ✅ FastAPI app with lifespan
app = FastAPI(
    title="ContractGuard.ai - AI Contract Review Platform API",
    description="Production-ready AI contract review and analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# 🔌 Include routers
from routes import auth, billing, contracts, analytics, settings as user_settings

app.include_router(auth.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")  # Enable analytics for dashboard
app.include_router(user_settings.router, prefix="/api/user-settings")  # More specific routes first
app.include_router(contracts.router, prefix="/api")  # Generic routes last

# 🔒 Security Middleware
if settings.environment == "production":
    # Trusted hosts middleware for production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domain in production
    )

# 🌐 CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 🚀 Rate limiting middleware
rate_limiter = RateLimiter(requests_per_minute=100)
app.middleware("http")(rate_limit_middleware(rate_limiter))

# 📊 Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests for monitoring and debugging."""
    start_time = time.time()
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Log request start
    log_api_request(
        logger=logger,
        method=request.method,
        path=str(request.url.path),
        status_code=0,  # 0 indicates request started
        response_time=0.0,  # 0 for request start
        ip_address=client_ip
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        request_count.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)
        
        # Log successful request
        log_api_request(
            logger=logger,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            response_time=duration,
            ip_address=client_ip
        )
        
        return response
        
    except Exception as e:
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        request_count.labels(method=request.method, endpoint=request.url.path, status=500).inc()
        request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)
        
        # Log error
        log_error(
            logger=logger,
            error=e,
            context={
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "duration": duration
            }
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# 🔧 Exception handler
app.add_exception_handler(ContractGuardAIException, custom_exception_handler)

# 📁 Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🏥 Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "ContractGuard.ai API"
    }

# 📊 Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for monitoring."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# 🔥 Cache management endpoints
@app.post("/api/cache/warm")
async def warm_cache_endpoint():
    """Warm up the cache with frequently accessed data."""
    try:
        warm_cache()
        return {"message": "Cache warming completed successfully"}
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        return {"message": "Cache warming failed", "error": str(e)}

@app.get("/api/cache/stats")
async def cache_stats_endpoint():
    """Get cache statistics for monitoring."""
    try:
        stats = get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"error": "Failed to get cache stats"}

# 🔍 Schema validation on startup
@app.on_event("startup")
async def verify_schemas():
    """Verify that all Pydantic schemas are valid on startup."""
    try:
        # Import all schemas to validate them
        from schemas import (
            UserCreate, UserOut, UserInfo,
            WorkspaceCreate, WorkspaceOut, WorkspaceInfo,
            ContractRecordCreate, ContractRecordOut, ContractRecordList,
            LoginRequest, LoginResponse,
            DashboardMetrics
        )
        logger.info("✅ All Pydantic schemas validated successfully")
    except Exception as e:
        logger.error(f"❌ Schema validation failed: {e}")
        raise e

# 🎯 Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to ContractGuard.ai API",
        "version": "1.0.0",
        "description": "AI Contract Review Platform",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

# 🚀 Startup message
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting ContractGuard.ai API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


