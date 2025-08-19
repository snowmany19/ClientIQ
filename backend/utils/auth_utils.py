# utils/auth_utils.py

import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from core.config import get_settings
from utils.password_validator import PasswordValidator
from utils.logger import get_logger

# Get settings
settings = get_settings()

# Initialize logger
logger = get_logger("auth")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password validator
password_validator = PasswordValidator(
    min_length=settings.password_min_length,
    require_uppercase=settings.password_require_uppercase,
    require_lowercase=settings.password_require_lowercase,
    require_digits=settings.password_require_digits,
    require_special=settings.password_require_special
)

# OAuth2 scheme for JWT extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Hash a plain password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password against its hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Validate password strength
def validate_password(password: str) -> tuple[bool, list[str]]:
    """Validate password and return (is_valid, list_of_errors)."""
    return password_validator.validate(password)

# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_expiration_minutes))
    to_encode.update({"exp": expire})
    
    try:
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    except Exception as e:
        logger.error(f"Failed to create JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authentication token"
        )

# Decode JWT token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}")
        return None

# Dependency to get the current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"User not found: {username}")
        raise credentials_exception
    
    return user

# Dependency to require a specific role (RBAC)
def require_role(*roles):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            logger.warning(f"Insufficient permissions: user_id={user.id}, required_roles={roles}, actual_role={user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role(s): {roles}"
            )
        return user
    return role_checker

# Dependency to require active subscription
def require_active_subscription(user: User = Depends(get_current_user)):
    # 🎯 Admins bypass billing - they always have full access
    if user.role == "admin":
        return user
    
    # Check subscription status for non-admin users
    if user.subscription_status not in ["active", "trialing"]:
        logger.warning(f"Subscription required: user_id={user.id}, subscription_status={user.subscription_status}")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required. Please subscribe to continue."
        )
    return user
