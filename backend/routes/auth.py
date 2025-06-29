# routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

import sys
import pathlib

# 🛠 Fix import path if run from main.py
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from database import get_db
from models import User, Store
from schemas import Token, UserInfo, UserCreate
from utils.auth_utils import (
    verify_password, create_access_token, get_password_hash, get_current_user
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

def create_access_token(data: dict, expires_delta: timedelta = None):
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
    if user.store_id and user.store:
        store_info = {
            "id": user.store.id,
            "store_number": f"Store #{user.store.id:03d}",  # Format as Store #001, #002, etc.
            "name": user.store.name,
            "location": user.store.location
        }

    return {
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
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


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


