# backend/main.py

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 👇 Fix path issues for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base

# ✅ FastAPI app must be defined BEFORE routers are included
app = FastAPI(title="IncidentIQ API")

# 🔌 Include routers
from routes import auth, incidents, billing
app.include_router(auth.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(billing.router, prefix="/api")

# 🧱 Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# 📁 Ensure static folders exist
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/reports", exist_ok=True)

# 🌐 Enable CORS
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

# ✅ Health check
@app.get("/")
def read_root():
    return {"message": "IncidentIQ backend is operational."}


