# routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import os

import sys
import pathlib

# 🛠 Fix import path if run from main.py
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from database import get_db
from models import User, Workspace, UserSession
from schemas import Token, UserInfo, UserCreate, UserUpdate
from utils.auth_utils import (
    verify_password, create_access_token, get_password_hash, get_current_user, 
    require_role, validate_password
)

from utils.logger import get_logger, log_security_event
from core.config import get_settings
from utils.validation import InputValidator, ValidationException
from utils.password_validator import PasswordValidator
import secrets

# Get settings and logger
settings = get_settings()
logger = get_logger("auth")

router = APIRouter(tags=["Auth"])

# 🔐 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 🔧 Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# 🚪 POST /login
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
    request: Request = None
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        if request:
            client_ip = request.client.host if request.client else "unknown"
            log_security_event(
                logger,
                event_type="failed_login",
                user_id=str(None),
                ip_address=client_ip,
                details={"username": form_data.username}
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful login
    if request:
        client_ip = request.client.host if request.client else "unknown"
        # Log successful login (security event logging removed for now)

    # Update user activity timestamps
    user.last_login_at = datetime.utcnow()
    user.last_activity_at = datetime.utcnow()
    
    # Create session record
    session_token = secrets.token_urlsafe(32)
    session_expires = datetime.utcnow() + timedelta(days=30)  # 30 day session
    
    # Get device info from user agent
    user_agent = request.headers.get("user-agent", "Unknown") if request else "Unknown"
    device_info = "Unknown Device"
    if "Chrome" in user_agent:
        device_info = "Chrome Browser"
    elif "Safari" in user_agent:
        device_info = "Safari Browser"
    elif "Firefox" in user_agent:
        device_info = "Firefox Browser"
    elif "Mobile" in user_agent:
        device_info = "Mobile Device"
    
    new_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        device_info=device_info,
        ip_address=request.client.host if request and request.client else None,
        user_agent=user_agent,
        expires_at=session_expires
    )
    
    db.add(new_session)
    db.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 👤 GET /me — Retrieve current user info
@router.get("/me", response_model=UserInfo)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🎯 Admins always have "active" subscription status
    subscription_status = "active" if user.role == "admin" else user.subscription_status

    return {
        "id": user.id,
        "username": user.username, 
        "email": user.email, 
        "role": user.role,
        "subscription_status": subscription_status,
        "plan_id": user.plan_id,
    }


# 🆕 POST /register — Create a new user
@router.post("/register", response_model=UserInfo)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Centralized input validation
    try:
        validated_username = InputValidator.validate_username(user.username)
        validated_email = InputValidator.validate_email(user.email) if user.email else None
        validated_password = InputValidator.validate_password(user.password)
    except ValidationException as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    is_valid, errors = PasswordValidator().validate(validated_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(errors)}"
        )
    
    db_user = db.query(User).filter(User.username == validated_username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(validated_password)
    new_user = User(
        username=validated_username,
        hashed_password=hashed_pw,
        email=validated_email,
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=user.company_name,
        phone=user.phone,
        role=user.role or "inspector",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "subscription_status": new_user.subscription_status,
        "plan_id": new_user.plan_id
    }


# 👥 POST /users/create — Create user with role-based permissions
@router.post("/users/create", response_model=UserInfo)
def create_user_with_permissions(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user with role-based permissions:
    - Admins can create all roles (admin, staff, employee)
    - Pro users can create staff and employee roles (max 5 users per org/plan)
    - Employees cannot create users
    - New users inherit creator's plan and subscription status
    """
    # Centralized input validation
    try:
        validated_username = InputValidator.validate_username(user.username)
        validated_email = InputValidator.validate_email(user.email) if user.email else None
        validated_password = InputValidator.validate_password(user.password)
    except ValidationException as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # 🔐 Check if current user can create users
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees cannot create new users. Please contact your administrator."
        )
    
    # 🔐 Check if current user can create the requested role
    if current_user.role == "staff":
        if user.role not in ["employee"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff users can only create employee accounts."
            )
    elif current_user.role == "admin":
        if user.role not in ["admin", "staff", "employee"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be admin, staff, or employee."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users."
        )
    
    # 🔍 Check if username/email already exists
    existing_user = db.query(User).filter(User.username == validated_username).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    
    if validated_email is not None:
        existing_email = db.query(User).filter(User.email == validated_email).first()
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
    
    # Validate password strength
    is_valid, errors = PasswordValidator().validate(validated_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(errors)}"
        )
    
    # 🚦 Enforce Pro user limit (max 5 users per org/plan)
    if current_user.plan_id == "pro":
        pro_user_count = db.query(User).filter(User.plan_id == "pro", User.subscription_status == "active").count()
        if pro_user_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pro plan allows a maximum of 5 users. Upgrade to Enterprise for unlimited users."
            )
    
    # 🏗️ Create the new user, inheriting plan/subscription from creator
    hashed_password = get_password_hash(validated_password)
    new_user = User(
        username=validated_username,
        hashed_password=hashed_password,
        email=validated_email,
        role=user.role,
        plan_id=current_user.plan_id,
        subscription_status=current_user.subscription_status
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log user creation
        logger.info(f"User created: created_by={current_user.id}, new_user_id={new_user.id}, role={new_user.role}")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "subscription_status": new_user.subscription_status,
            "plan_id": new_user.plan_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user: {str(e)} (created_by={current_user.id})", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

# 👤 POST /users/change-password — Change own password
@router.post("/users/change-password")
def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Allow any user to change their own password.
    """
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect."
        )
    
    # Validate new password strength
    is_valid, errors = PasswordValidator().validate(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(errors)}"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    
    # Log password change
    logger.info("Password changed", user_id=str(current_user.id))
    
    return {"message": "Password updated successfully."}

# 👥 GET /users — List users (admin/staff only)
@router.get("/users", response_model=List[UserInfo])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List users with role-based filtering:
    - Admins can see all users
    - Staff can only see users from their store
    - Employees cannot access this endpoint
    """
    # Check permissions
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees cannot view user management."
        )
    
    # Build query based on role
    if current_user.role == "admin":
        # Admins can see all users
        users_query = db.query(User)
    elif current_user.role == "staff":
        # Staff can only see users from their store
        if current_user.workspace_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff must be assigned to a workspace to view users."
            )
        users_query = db.query(User).filter(User.workspace_id == current_user.workspace_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view users."
        )
    
    # Apply pagination and get results
    users = users_query.offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        result.append({
            "id": user.id,  # Add user ID for frontend operations
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "subscription_status": user.subscription_status,
            "plan_id": user.plan_id,
        })
    
    return result


# 🛠️ One-time default user creator (run manually if needed)
@router.get("/seed-users")
def seed_default_users(db: Session = Depends(get_db)):
    # First, create some sample workspaces
    workspaces = [
        {"name": "Downtown Legal", "company_name": "Downtown Legal Services", "industry": "Legal"},
        {"name": "Mall Corp", "company_name": "Mall Corporation", "industry": "Retail"},
        {"name": "Suburban Tech", "company_name": "Suburban Tech Solutions", "industry": "Technology"},
    ]

    created_workspaces = []
    for workspace_data in workspaces:
        existing_workspace = db.query(Workspace).filter(Workspace.name == workspace_data["name"]).first()
        if not existing_workspace:
            workspace = Workspace(
                name=workspace_data["name"], 
                company_name=workspace_data["company_name"],
                industry=workspace_data["industry"]
            )
            db.add(workspace)
            db.commit()
            created_workspaces.append(workspace_data["name"])

    # Now create users with workspace assignments
    defaults = [
        {"username": "admin", "password": "Admin123!", "role": "admin", "workspace_id": None},  # Admin has no workspace restriction
        {"username": "manager1", "password": "Manager123!", "role": "staff", "workspace_id": 1},   # Staff at Downtown Legal
        {"username": "manager2", "password": "Manager123!", "role": "staff", "workspace_id": 2},   # Staff at Mall Corp
        {"username": "employee1", "password": "Employee123!", "role": "employee", "workspace_id": 1}, # Employee at Downtown Legal
        {"username": "employee2", "password": "Employee123!", "role": "employee", "workspace_id": 2}, # Employee at Mall Corp
    ]
    created = []

    for user in defaults:
        if not db.query(User).filter(User.username == user["username"]).first():
            db_user = User(
                username=user["username"],
                hashed_password=get_password_hash(user["password"]),
                role=user["role"],
                workspace_id=user["workspace_id"]
            )
            db.add(db_user)
            created.append(user["username"])
    db.commit()

    return {
        "created_workspaces": created_workspaces if created_workspaces else "All workspaces already exist",
        "created_users": created if created else "All default users already exist."
    }

# 👤 PUT /users/{user_id} — Edit user
@router.put("/users/{user_id}", response_model=UserInfo)
def edit_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit user details (admin/super_admin only)
    """

    
    # Get user to edit
    user_to_edit = db.query(User).filter(User.id == user_id).first()
    if not user_to_edit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check permissions - only admin and super_admin can edit users
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can edit users."
        )
    
    # Update user fields
    if user_update.username != user_to_edit.username:
        existing = db.query(User).filter(User.username == user_update.username).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists."
            )
        user_to_edit.username = user_update.username
    
    if user_update.email is not None and user_update.email != user_to_edit.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )
        user_to_edit.email = user_update.email
    
    user_to_edit.role = user_update.role
    
    # Update password if provided
    if user_update.password is not None:
        if len(user_update.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )
        # Validate password strength
        is_valid, errors = PasswordValidator().validate(user_update.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )
        user_to_edit.hashed_password = get_password_hash(user_update.password)
    
    try:
        db.commit()
        db.refresh(user_to_edit)
        
        return {
            "id": user_to_edit.id,
            "username": user_to_edit.username,
            "email": user_to_edit.email,
            "role": user_to_edit.role,
            "subscription_status": user_to_edit.subscription_status,
            "plan_id": user_to_edit.plan_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

# 👤 DELETE /users/{user_id} — Delete user (soft delete)
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete user (admin/staff only) - preserves violations
    """
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees cannot delete users."
        )
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account."
        )
    
    # Get user to delete
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check permissions
    if current_user.role == "staff":
        if user_to_delete.role not in ["employee"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff can only delete employee accounts."
            )
    
    # Soft delete by setting subscription to inactive and clearing sensitive data
    user_to_delete.subscription_status = "inactive"
    user_to_delete.email = None
    user_to_delete.hashed_password = "DELETED"
    user_to_delete.username = f"deleted_{user_to_delete.username}_{user_id}"
    
    try:
        db.commit()
        return {"message": "User deleted successfully. Violations are preserved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.post("/change-password")
def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current and new password are required")
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    hashed_new_password = get_password_hash(new_password)
    
    # Update password
    current_user.hashed_password = hashed_new_password
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.get("/admin/users")
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "subscription_status": user.subscription_status,
            "workspace_id": user.workspace_id
        }
        for user in users
    ]

@router.post("/admin/users")
def create_user(
    user_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role")
    workspace_id = user_data.get("workspace_id")
    
    if not all([username, email, password, role]):
        raise HTTPException(status_code=400, detail="All fields are required")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
        workspace_id=workspace_id,
        subscription_status="active"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "subscription_status": new_user.subscription_status,
        "workspace_id": new_user.workspace_id
    }

@router.put("/admin/users/{user_id}")
def update_user(
    user_id: int,
    user_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if "username" in user_data:
        user.username = user_data["username"]
    if "email" in user_data:
        user.email = user_data["email"]
    if "role" in user_data:
        user.role = user_data["role"]
    if "workspace_id" in user_data:
        user.workspace_id = user_data["workspace_id"]
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "subscription_status": user.subscription_status,
        "workspace_id": user.workspace_id
    }

@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


