# CRUD operations
# crud.py
# Reusable database operations for IncidentIQ (CRUD: Create, Read, Update, Delete)

from sqlalchemy.orm import Session
from incidentiq import models, schemas
from typing import List, Optional
from datetime import datetime


# 🔍 Get all incidents with optional filters
def get_incidents(db: Session, skip: int = 0, limit: int = 100, store_id: Optional[int] = None) -> List[models.Incident]:
    query = db.query(models.Incident)
    if store_id:
        query = query.filter(models.Incident.store_id == store_id)
    return query.order_by(models.Incident.timestamp.desc()).offset(skip).limit(limit).all()

# 🔍 Get single incident by ID
def get_incident(db: Session, incident_id: int) -> Optional[models.Incident]:
    return db.query(models.Incident).filter(models.Incident.id == incident_id).first()

# ➕ Create new incident
def create_incident(db: Session, incident: schemas.IncidentCreate) -> models.Incident:
    db_incident = models.Incident(
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

# 📝 Update an existing incident
def update_incident(db: Session, incident_id: int, updates: dict) -> Optional[models.Incident]:
    db_incident = get_incident(db, incident_id)
    if not db_incident:
        return None
    for key, value in updates.items():
        setattr(db_incident, key, value)
    db.commit()
    db.refresh(db_incident)
    return db_incident

# ❌ Delete incident
def delete_incident(db: Session, incident_id: int) -> bool:
    db_incident = get_incident(db, incident_id)
    if not db_incident:
        return False
    db.delete(db_incident)
    db.commit()
    return True


# ----------- Users -----------

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        store_id=user.store_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ----------- Stores -----------

def get_all_stores(db: Session) -> List[models.Store]:
    return db.query(models.Store).all()

def create_store(db: Session, store: schemas.StoreCreate) -> models.Store:
    db_store = models.Store(name=store.name, location=store.location)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


# ----------- Offenders -----------

def get_offenders(db: Session) -> List[models.Offender]:
    return db.query(models.Offender).all()

def create_offender(db: Session, offender: schemas.OffenderCreate) -> models.Offender:
    db_offender = models.Offender(alias=offender.alias, notes=offender.notes)
    db.add(db_offender)
    db.commit()
    db.refresh(db_offender)
    return db_offender
