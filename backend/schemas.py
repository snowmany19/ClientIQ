# schemas.py
# ✅ Pydantic schemas for A.I.ncident📊 - AI Incident Management Dashboard

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

# ===========================
# ✅ Store Schemas
# ===========================

class StoreBase(BaseModel):
    name: str = Field(..., description="Store name")
    location: str = Field(..., description="Store location/address")

class StoreCreate(StoreBase):
    pass

class StoreOut(StoreBase):
    id: int = Field(..., description="Unique store identifier")
    class Config:
        orm_mode = True

class StoreInfo(BaseModel):
    id: int = Field(..., description="Unique store identifier")
    store_number: str = Field(..., description="Formatted store number")
    name: str = Field(..., description="Store name")
    location: str = Field(..., description="Store location/address")

# ===========================
# ✅ User Schemas
# ===========================

ValidRoles = Literal["admin", "staff", "employee"]

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username (3-20 chars, alphanumeric + underscore)")
    email: Optional[EmailStr] = Field(None, description="User email address")
    role: Optional[ValidRoles] = Field(default="employee", description="User role in the system")
    store_id: Optional[int] = Field(None, description="Assigned store ID")

class UserCreate(UserBase):
    password: str = Field(..., description="User password (min 8 chars)")

class UserOut(UserBase):
    id: int = Field(..., description="Unique user identifier")
    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User username")
    email: Optional[EmailStr] = Field(None, description="User email address")
    role: ValidRoles = Field(..., description="User role")
    subscription_status: Optional[str] = Field(default="inactive", description="Current subscription status")
    plan_id: Optional[str] = Field(default="basic", description="Current plan")
    store: Optional[StoreInfo] = Field(None, description="Assigned store information")

# ===========================
# ✅ Offender Schemas
# ===========================

class OffenderBase(BaseModel):
    alias: str = Field(..., description="Offender alias or nickname")
    notes: Optional[str] = Field(None, description="Additional notes about the offender")

class OffenderCreate(OffenderBase):
    pass

class OffenderOut(OffenderBase):
    id: int = Field(..., description="Unique offender identifier")
    class Config:
        orm_mode = True

# ===========================
# ✅ Incident Schemas
# ===========================

class IncidentBase(BaseModel):
    description: str = Field(..., description="Detailed incident description")
    summary: Optional[str] = Field(None, description="AI-generated summary of the incident")
    tags: Optional[str] = Field(None, description="Comma-separated incident tags")
    image_url: Optional[str] = Field(None, description="URL to incident image")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF report")
    store_id: Optional[int] = Field(None, description="Store where incident occurred")
    user_id: Optional[int] = Field(None, description="User who reported the incident")
    offender_id: Optional[int] = Field(None, description="Associated offender ID")

class IncidentCreate(IncidentBase):
    pass

class IncidentOut(BaseModel):
    id: int = Field(..., description="Unique incident identifier")
    timestamp: datetime = Field(..., description="When the incident was reported")
    description: str = Field(..., description="Detailed incident description")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    severity: Optional[str] = Field(None, description="Incident severity level")
    store_name: Optional[str] = Field(None, description="Store name where incident occurred")
    location: Optional[str] = Field(None, description="Specific location within store")
    offender: Optional[str] = Field(None, description="Offender description")
    pdf_path: Optional[str] = Field(None, description="Path to PDF report")
    image_url: Optional[str] = Field(None, description="Path to incident image")
    user_id: Optional[int] = Field(None, description="User who reported the incident")
    reported_by: Optional[str] = Field(None, description="Username of person who reported")

    class Config:
        orm_mode = True

class IncidentList(BaseModel):
    incidents: List[IncidentOut] = Field(..., description="List of incidents")

# ===========================
# ✅ Token Schema (for login)
# ===========================

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username from token")
    role: Optional[ValidRoles] = Field(None, description="User role from token")

# ===========================
# ✅ Request/Response Models for Better API Docs
# ===========================

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")
    user: UserInfo = Field(..., description="User information")

class IncidentCreateRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed incident description")
    store: str = Field(..., description="Store name in format 'Store #XXX'")
    location: str = Field(..., min_length=2, max_length=100, description="Specific location within store")
    offender: str = Field(..., min_length=2, max_length=100, description="Offender description")

class PaginationInfo(BaseModel):
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    items_per_page: int = Field(..., description="Items per page")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    errors: Optional[List[dict]] = Field(None, description="Detailed validation errors")

class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


