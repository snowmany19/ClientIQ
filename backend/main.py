# backend/main.py

import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# 👇 Fix path issues for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from core.config import get_settings
from utils.logger import setup_logging, get_logger, log_api_request, log_error
from utils.rate_limiter import RateLimiter, rate_limit_middleware, get_client_ip

# Get settings
settings = get_settings()

# Setup logging
logger = setup_logging(settings.log_level, settings.log_file)

# Initialize rate limiter
rate_limiter = RateLimiter(settings.rate_limit_requests)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting IncidentIQ backend...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create static directories
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("IncidentIQ backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IncidentIQ backend...")

# ✅ FastAPI app with lifespan
app = FastAPI(
    title="IncidentIQ API",
    description="Production-ready incident management API",
    version="1.0.0",
    lifespan=lifespan
)

# 🔌 Include routers
from routes import auth, incidents, billing
app.include_router(auth.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(billing.router, prefix="/api")

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
    allow_origins=[
        "http://localhost:8501",  # Streamlit default port
        "http://127.0.0.1:8501",  # Alternative localhost
        "http://localhost:3000",  # React default (if using React frontend)
        "http://127.0.0.1:3000",  # Alternative React localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 📂 Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# 📊 Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log successful request
        log_api_request(
            logger,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Log error
        log_error(
            logger,
            error=e,
            context={
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": client_ip,
                "duration": duration
            }
        )
        
        # Re-raise the exception
        raise

# ✅ Health check
@app.get("/")
def read_root():
    return {"message": "IncidentIQ backend is operational.", "version": "1.0.0"}

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

# 🚀 Startup delay for development
if settings.environment == "development":
    import asyncio
    asyncio.create_task(asyncio.sleep(1))  # Small delay for development


