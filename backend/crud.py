# CRUD operations
# crud.py
# Reusable database operations for CivicLogHOA - HOA Violation Management Platform (CRUD: Create, Read, Update, Delete)

from sqlalchemy.orm import Session
from typing import List, Optional
from models import Violation, User, HOA, Resident

# 🔍 Get all violations with optional filters
def get_violations(db: Session, skip: int = 0, limit: int = 100, hoa_id: Optional[int] = None) -> List[Violation]:
    query = db.query(Violation)
    if hoa_id:
        query = query.filter(Violation.hoa_id == hoa_id)
    return query.order_by(Violation.timestamp.desc()).offset(skip).limit(limit).all()

# 🔍 Get single violation by ID
def get_violation(db: Session, violation_id: int) -> Optional[Violation]:
    return db.query(Violation).filter(Violation.id == violation_id).first()

# ➕ Create new violation
def create_violation(db: Session, violation_data: dict) -> Violation:
    db_violation = Violation(**violation_data)
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation

# 🗑️ Delete violation
def delete_violation(db: Session, violation_id: int) -> bool:
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if violation:
        db.delete(violation)
        db.commit()
        return True
    return False

# 👤 User operations
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_by_hoa(db: Session, hoa_id: int) -> List[User]:
    return db.query(User).filter(User.hoa_id == hoa_id).all()

# 🏘️ HOA operations
def get_hoa(db: Session, hoa_id: int) -> Optional[HOA]:
    return db.query(HOA).filter(HOA.id == hoa_id).first()

def get_all_hoas(db: Session) -> List[HOA]:
    return db.query(HOA).all()

def create_hoa(db: Session, name: str, location: str, contact_email: Optional[str] = None, contact_phone: Optional[str] = None) -> HOA:
    db_hoa = HOA(
        name=name,
        location=location,
        contact_email=contact_email,
        contact_phone=contact_phone
    )
    db.add(db_hoa)
    db.commit()
    db.refresh(db_hoa)
    return db_hoa

# 🧑‍🚨 Resident operations
def get_resident(db: Session, resident_id: int) -> Optional[Resident]:
    return db.query(Resident).filter(Resident.id == resident_id).first()

def get_residents_by_hoa(db: Session, hoa_id: int) -> List[Resident]:
    return db.query(Resident).filter(Resident.hoa_id == hoa_id).all()

def create_resident(db: Session, name: str, address: str, hoa_id: int, email: Optional[str] = None, phone: Optional[str] = None, notes: Optional[str] = None) -> Resident:
    db_resident = Resident(
        name=name,
        address=address,
        hoa_id=hoa_id,
        email=email,
        phone=phone,
        notes=notes
    )
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)
    return db_resident

def update_resident_violation_count(db: Session, resident_id: int) -> None:
    """Update the violation count for a resident."""
    resident = get_resident(db, resident_id)
    if resident:
        # Use SQLAlchemy update to avoid type issues
        db.query(Resident).filter(Resident.id == resident_id).update(
            {"violation_count": Resident.violation_count + 1}
        )
        db.commit()
