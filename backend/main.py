# backend/main.py

import os
import sys
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# 👇 Fix path issues for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, get_db
from models import Incident
from schemas import IncidentOut
from utils.summary_generator import summarize_incident, classify_severity
from utils.image_uploader import save_image
from utils.pdf import generate_pdf

# ✅ FastAPI app must be defined BEFORE routers are included
app = FastAPI(title="IncidentIQ API")

# 🔌 Include auth router
from routes import auth
app.include_router(auth.router, prefix="/auth")  # ✅ Adds /auth/login, /auth/register, etc.


# 🧱 Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# 📁 Ensure static folders exist
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/reports", exist_ok=True)

# 🌐 Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Health check
@app.get("/")
def read_root():
    return {"message": "IncidentIQ backend is operational."}

# 📝 Create new incident
@app.post("/incidents/")
def create_incident(
    description: str = Form(...),
    store: str = Form(...),
    location: str = Form(...),
    offender: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    image_path = save_image(file) if file else None
    summary, tags = summarize_incident(description)
    severity = classify_severity(summary)

    incident_data = {
        "id": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "store": store,
        "location": location,
        "offender": offender,
        "tags": tags,
        "description": description,
        "summary": summary,
        "image_path": image_path
    }

    pdf_path = generate_pdf(incident_data)

    incident = Incident(
        description=description,
        summary=summary,
        tags=tags,
        severity=severity,
        image_url=image_path,
        pdf_path=pdf_path,
        store_name=store,
        location=location,
        offender=offender,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "summary": summary,
        "tags": tags,
        "pdf_path": pdf_path,
        "timestamp": incident.timestamp.isoformat(),
    }

# 📄 Get all incidents
@app.get("/incidents/", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()


