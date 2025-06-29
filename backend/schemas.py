# schemas.py
# ✅ Pydantic schemas for IncidentIQ

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# ===========================
# ✅ Store Schemas
# ===========================

class StoreBase(BaseModel):
    name: str
    location: str

class StoreCreate(StoreBase):
    pass

class StoreOut(StoreBase):
    id: int
    class Config:
        orm_mode = True

class StoreInfo(BaseModel):
    id: int
    store_number: str
    name: str
    location: str

# ===========================
# ✅ User Schemas
# ===========================

ValidRoles = Literal["admin", "staff", "employee"]

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: Optional[ValidRoles] = "employee"
    store_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    role: ValidRoles
    subscription_status: Optional[str] = "inactive"
    plan_id: Optional[str] = "basic"
    store: Optional[StoreInfo] = None


# ===========================
# ✅ Offender Schemas
# ===========================

class OffenderBase(BaseModel):
    alias: str
    notes: Optional[str] = None

class OffenderCreate(OffenderBase):
    pass

class OffenderOut(OffenderBase):
    id: int
    class Config:
        orm_mode = True


# ===========================
# ✅ Incident Schemas
# ===========================

class IncidentBase(BaseModel):
    description: str
    summary: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    pdf_path: Optional[str] = None
    store_id: Optional[int] = None
    user_id: Optional[int] = None
    offender_id: Optional[int] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentOut(BaseModel):
    id: int
    timestamp: datetime
    description: str
    summary: Optional[str]
    tags: Optional[str]
    severity: Optional[str]
    store_name: Optional[str]
    location: Optional[str]
    offender: Optional[str]
    pdf_path: Optional[str]
    image_url: Optional[str]
    user_id: Optional[int]
    reported_by: Optional[str]  # Username of the person who reported

    class Config:
        orm_mode = True

class IncidentList(BaseModel):
    incidents: List[IncidentOut]


# ===========================
# ✅ Token Schema (for login)
# ===========================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[ValidRoles] = None


