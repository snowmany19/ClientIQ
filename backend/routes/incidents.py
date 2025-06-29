# Incident routes
# routes/incidents.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import Incident, User, Store
from schemas import IncidentCreate, IncidentOut
from utils.auth_utils import get_current_user, require_role, decode_token, require_active_subscription
from utils.image_uploader import save_image
from utils.pdf import generate_pdf
from utils.summary_generator import summarize_incident, classify_severity
from utils.email_alerts import send_email_alert

router = APIRouter(prefix="/incidents", tags=["Incidents"])

# 🔐 RBAC: Check if user can access store data
def can_access_store(user: User, store_name: str, db: Session) -> bool:
    if user.role == "admin":
        return True  # Admins can access all stores
    
    if user.role in ["employee", "staff"]:
        # Check if user's store matches the incident store
        if user.store_id is not None:
            user_store = db.query(Store).filter(Store.id == user.store_id).first()
            if user_store and user_store.name == store_name:
                return True
        # Fallback: check if store_name matches user's assigned store
        return getattr(user, 'store_name', None) == store_name
    
    return False

@router.post("/", response_model=IncidentOut)
def create_incident(
    description: str = Form(...),
    store: str = Form(...),
    location: str = Form(...),
    offender: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    # 🔍 Input Validation
    if not description or len(description.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must be at least 10 characters long."
        )
    
    if len(description) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must be less than 2000 characters."
        )
    
    # Basic validation - just ensure fields are not empty
    if not store or not store.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store name is required."
        )
    
    if not location or not location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required."
        )
    
    # File validation
    if file:
        # Check file size (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB."
            )
        
        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG and PNG files are allowed."
            )
    
    # 🔐 RBAC: Check if user can submit incidents for this store
    if not can_access_store(current_user, store, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. You can only submit incidents for your assigned store."
        )
    
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
        "image_path": image_path,
        "username": current_user.username
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
        user_id=current_user.id,  # ✅ Associate with authenticated user
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "timestamp": incident.timestamp,
        "description": incident.description,
        "summary": summary,
        "tags": tags,
        "severity": incident.severity,
        "store_name": incident.store_name,
        "location": incident.location,
        "offender": incident.offender,
        "pdf_path": pdf_path,
        "image_url": incident.image_url,
        "user_id": incident.user_id,
        "reported_by": current_user.username,
    }

@router.get("/", response_model=List[IncidentOut])
def get_all_incidents(
    skip: int = 0,
    limit: int = 50,
    store_id: Optional[int] = None,
    tag: Optional[str] = None,
    offender_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    # 🔍 Input validation for pagination
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip must be 0 or greater."
        )
    
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100."
        )
    
    # 🔐 RBAC: Filter incidents based on user role
    if current_user.role == "admin":
        # Admins can see all incidents
        query = db.query(Incident)
    elif current_user.role in ["employee", "staff"]:
        # Employees and staff can only see incidents from their store
        if current_user.store_id is not None:
            user_store = db.query(Store).filter(Store.id == current_user.store_id).first()
            if user_store:
                query = db.query(Incident).filter(Incident.store_name == user_store.name)
            else:
                # Fallback: no store assigned, return empty
                return []
        else:
            # No store assigned, return empty
            return []
    else:
        # Unknown role, return empty
        return []
    
    # Apply additional filters
    if store_id:
        query = query.filter(Incident.store_id == store_id)
    if tag:
        query = query.filter(Incident.tags.ilike(f"%{tag}%"))
    if offender_id:
        query = query.filter(Incident.offender_id == offender_id)
    
    # Apply pagination
    incidents = query.order_by(Incident.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Add reported_by information to each incident
    for incident in incidents:
        if incident.user:
            incident.reported_by = incident.user.username
        else:
            incident.reported_by = "Unknown"
    
    return incidents

# 🔐 RBAC: Get user's accessible stores
@router.get("/stores/accessible")
def get_accessible_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        # Admins can access all stores
        stores = db.query(Store).all()
        return [{"id": store.id, "store_number": f"Store #{store.id:03d}", "name": store.name, "location": store.location} for store in stores]
    elif current_user.role in ["employee", "staff"]:
        # Employees and staff can only access their assigned store
        if current_user.store_id is not None:
            store = db.query(Store).filter(Store.id == current_user.store_id).first()
            if store:
                return [{"id": store.id, "store_number": f"Store #{store.id:03d}", "name": store.name, "location": store.location}]
        return []
    else:
        return []

# 🔐 RBAC: Get pagination info for incidents
@router.get("/pagination-info")
def get_pagination_info(
    store_id: Optional[int] = None,
    tag: Optional[str] = None,
    offender_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 🔐 RBAC: Filter incidents based on user role (same logic as get_all_incidents)
    if current_user.role == "admin":
        query = db.query(Incident)
    elif current_user.role in ["employee", "staff"]:
        if current_user.store_id is not None:
            user_store = db.query(Store).filter(Store.id == current_user.store_id).first()
            if user_store:
                query = db.query(Incident).filter(Incident.store_name == user_store.name)
            else:
                return {"total": 0, "pages": 0}
        else:
            return {"total": 0, "pages": 0}
    else:
        return {"total": 0, "pages": 0}
    
    # Apply additional filters
    if store_id:
        query = query.filter(Incident.store_id == store_id)
    if tag:
        query = query.filter(Incident.tags.ilike(f"%{tag}%"))
    if offender_id:
        query = query.filter(Incident.offender_id == offender_id)
    
    total = query.count()
    return {
        "total": total,
        "pages": (total + 49) // 50  # 50 items per page
    }

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident_by_id(
    incident_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # 🔐 RBAC: Check if user can access this specific incident
    if not can_access_store(current_user, str(incident.store_name), db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view incidents from your assigned store."
        )
    
    # Add reported_by information
    if incident.user:
        incident.reported_by = incident.user.username
    else:
        incident.reported_by = "Unknown"
    
    return incident
