# Incident routes
# routes/incidents.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import Incident, Store, User, Offender
from schemas import IncidentCreate, IncidentOut

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentOut)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(
        description=incident.description,
        summary=incident.summary,
        tags=incident.tags,
        timestamp=incident.timestamp or datetime.utcnow(),
        image_url=incident.image_url,
        pdf_path=incident.pdf_path,
        store_id=incident.store_id,
        user_id=incident.user_id,
        offender_id=incident.offender_id
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.get("/", response_model=List[IncidentOut])
def get_all_incidents(
    store_id: Optional[int] = None,
    tag: Optional[str] = None,
    offender_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if store_id:
        query = query.filter(Incident.store_id == store_id)
    if tag:
        query = query.filter(Incident.tags.ilike(f"%{tag}%"))
    if offender_id:
        query = query.filter(Incident.offender_id == offender_id)
    return query.order_by(Incident.timestamp.desc()).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident_by_id(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
