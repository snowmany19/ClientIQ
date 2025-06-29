# routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
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
from models import User, Store
from schemas import Token, UserInfo, UserCreate
from utils.auth_utils import (
    verify_password, create_access_token, get_password_hash, get_current_user, require_role
)
from utils.email_alerts import send_email_alert

router = APIRouter(tags=["Auth"])

# 🔐 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔑 JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 🔧 Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# 🚪 POST /login
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 👤 GET /me — Retrieve current user info
@router.get("/me", response_model=UserInfo)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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

    # 🏬 Get store information if assigned
    store_info = None
    if user.store_id is not None and user.store is not None:
        store_info = {
            "id": user.store.id,
            "store_number": f"Store #{user.store.id:03d}",  # Format as Store #001, #002, etc.
            "name": user.store.name,
            "location": user.store.location
        }

    return {
        "id": user.id,
        "username": user.username, 
        "email": user.email, 
        "role": user.role,
        "subscription_status": subscription_status,
        "plan_id": user.plan_id,
        "store": store_info
    }


# 🆕 POST /register — Create a new user
@router.post("/register", response_model=UserInfo)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_pw,
        email=user.email,
        role=user.role or "employee",
        store_id=user.store_id
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
    - Pro users can create staff and employee roles (max 5 users per org)
    - Employees cannot create users
    - New users inherit creator's plan and subscription status
    """
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
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
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
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=user.role,
        store_id=user.store_id,
        plan_id=current_user.plan_id,
        subscription_status=current_user.subscription_status
    )
    try:
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
    except Exception as e:
        db.rollback()
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
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long."
        )
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
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
        if current_user.store_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff must be assigned to a store to view users."
            )
        users_query = db.query(User).filter(User.store_id == current_user.store_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view users."
        )
    
    # Apply pagination and get results
    users = users_query.offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        # Get store information
        store_info = None
        if user.store_id is not None and user.store is not None:
            store_info = {
                "id": user.store.id,
                "store_number": f"Store #{user.store.id:03d}",
                "name": user.store.name,
                "location": user.store.location
            }
        
        result.append({
            "id": user.id,  # Add user ID for frontend operations
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "subscription_status": user.subscription_status,
            "plan_id": user.plan_id,
            "store": store_info
        })
    
    return result


# 🛠️ One-time default user creator (run manually if needed)
@router.get("/seed-users")
def seed_default_users(db: Session = Depends(get_db)):
    # First, create some sample stores
    stores = [
        {"name": "Downtown Store", "location": "123 Main St, Downtown"},
        {"name": "Mall Location", "location": "456 Shopping Ave, Mall"},
        {"name": "Suburban Branch", "location": "789 Oak Rd, Suburbs"},
    ]
    
    created_stores = []
    for store_data in stores:
        existing_store = db.query(Store).filter(Store.name == store_data["name"]).first()
        if not existing_store:
            store = Store(name=store_data["name"], location=store_data["location"])
            db.add(store)
            created_stores.append(store_data["name"])
    
    db.commit()
    
    # Now create users with store assignments
    defaults = [
        {"username": "admin", "password": "admin123", "role": "admin", "store_id": None},  # Admin has no store restriction
        {"username": "manager1", "password": "test123", "role": "staff", "store_id": 1},   # Staff at Downtown Store
        {"username": "manager2", "password": "test123", "role": "staff", "store_id": 2},   # Staff at Mall Location
        {"username": "employee1", "password": "test123", "role": "employee", "store_id": 1}, # Employee at Downtown Store
        {"username": "employee2", "password": "test123", "role": "employee", "store_id": 2}, # Employee at Mall Location
    ]
    created = []

    for user in defaults:
        if not db.query(User).filter(User.username == user["username"]).first():
            db_user = User(
                username=user["username"],
                hashed_password=get_password_hash(user["password"]),
                role=user["role"],
                store_id=user["store_id"]
            )
            db.add(db_user)
            created.append(user["username"])
    db.commit()

    return {
        "created_stores": created_stores if created_stores else "All stores already exist",
        "created_users": created if created else "All default users already exist."
    }

# 👤 PUT /users/{user_id} — Edit user
@router.put("/users/{user_id}", response_model=UserInfo)
def edit_user(
    user_id: int,
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit user details (admin/staff only)
    """
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees cannot edit users."
        )
    
    # Get user to edit
    user_to_edit = db.query(User).filter(User.id == user_id).first()
    if not user_to_edit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check permissions
    if current_user.role == "staff":
        if user_to_edit.role not in ["employee"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff can only edit employee accounts."
            )
        if user_update.role not in ["employee"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff can only assign employee roles."
            )
    
    # Update user fields
    if user_update.username != user_to_edit.username:
        existing = db.query(User).filter(User.username == user_update.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists."
            )
        user_to_edit.username = user_update.username
    
    if user_update.email and user_update.email != user_to_edit.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )
        user_to_edit.email = user_update.email
    
    user_to_edit.role = user_update.role
    user_to_edit.store_id = user_update.store_id
    
    # Update password if provided
    if user_update.password and len(user_update.password) >= 6:
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
    Soft delete user (admin/staff only) - preserves incidents
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
        return {"message": "User deleted successfully. Incidents are preserved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


