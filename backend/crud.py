# CRUD operations
# crud.py
# Reusable database operations for ContractGuard.ai - AI Contract Review Platform (CRUD: Create, Read, Update, Delete)

from sqlalchemy.orm import Session
from typing import List, Optional
from models import User, Workspace, ContractRecord

# 🔍 Get all contracts with optional filters
def get_contracts(db: Session, skip: int = 0, limit: int = 100, workspace_id: Optional[int] = None) -> List[ContractRecord]:
    query = db.query(ContractRecord)
    if workspace_id:
        query = query.filter(ContractRecord.workspace_id == workspace_id)
    return query.order_by(ContractRecord.created_at.desc()).offset(skip).limit(limit).all()

def get_contract(db: Session, contract_id: int) -> Optional[ContractRecord]:
    return db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()

def create_contract(db: Session, contract_data: dict) -> ContractRecord:
    db_contract = ContractRecord(**contract_data)
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def update_contract(db: Session, contract_id: int, contract_data: dict) -> Optional[ContractRecord]:
    db_contract = db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()
    if db_contract:
        for key, value in contract_data.items():
            setattr(db_contract, key, value)
        db.commit()
        db.refresh(db_contract)
    return db_contract

def delete_contract(db: Session, contract_id: int) -> bool:
    db_contract = db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()
    if db_contract:
        db.delete(db_contract)
        db.commit()
        return True
    return False

# 👥 User operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users_by_workspace(db: Session, workspace_id: int) -> List[User]:
    return db.query(User).filter(User.workspace_id == workspace_id).all()

def create_user(db: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# 🏢 Workspace operations
def get_workspace(db: Session, workspace_id: int) -> Optional[Workspace]:
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()

def get_all_workspaces(db: Session) -> List[Workspace]:
    return db.query(Workspace).all()

def create_workspace(db: Session, name: str, company_name: str, contact_email: Optional[str] = None, contact_phone: Optional[str] = None) -> Workspace:
    db_workspace = Workspace(
        name=name,
        company_name=company_name,
        contact_email=contact_email,
        contact_phone=contact_phone
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace

def update_workspace(db: Session, workspace_id: int, workspace_data: dict) -> Optional[Workspace]:
    db_workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if db_workspace:
        for key, value in workspace_data.items():
            setattr(db_workspace, key, value)
        db.commit()
        db.refresh(db_workspace)
    return db_workspace

def delete_workspace(db: Session, workspace_id: int) -> bool:
    db_workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if db_workspace:
        db.delete(db_workspace)
        db.commit()
        return True
    return False
