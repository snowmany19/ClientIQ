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

from database import get_db, SessionLocal
import models, schemas
from utils.auth_utils import decode_token, get_password_hash

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
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# 🚪 POST /login
@router.post("/login", response_model=schemas.Token)
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
@router.get("/me", response_model=schemas.UserInfo)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": user.username, "email": user.email, "role": user.role}


# 🆕 POST /register — Create a new user
@router.post("/register", response_model=schemas.UserInfo)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(
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
    defaults = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "employee", "password": "test123", "role": "employee"},
    ]
    created = []

    for user in defaults:
        if not db.query(models.User).filter(models.User.username == user["username"]).first():
            db_user = models.User(
                username=user["username"],
                hashed_password=get_password_hash(user["password"]),
                role=user["role"]
            )
            db.add(db_user)
            created.append(user["username"])
    db.commit()

    return {"created_users": created if created else "All default users already exist."}


