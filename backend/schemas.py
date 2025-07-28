# schemas.py
# ✅ Pydantic schemas for CivicLogHOA - HOA Violation Management

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

# ===========================
# ✅ HOA Schemas
# ===========================

class HOABase(BaseModel):
    name: str = Field(..., description="HOA name")
    location: str = Field(..., description="HOA location/address")
    contact_email: Optional[str] = Field(None, description="HOA contact email")
    contact_phone: Optional[str] = Field(None, description="HOA contact phone")
    logo_url: Optional[str] = Field(None, description="HOA logo URL")

class HOACreate(HOABase):
    pass

class HOAOut(HOABase):
    id: int = Field(..., description="Unique HOA identifier")
    class Config:
        orm_mode = True

class HOAInfo(BaseModel):
    id: int = Field(..., description="Unique HOA identifier")
    hoa_number: str = Field(..., description="Formatted HOA number")
    name: str = Field(..., description="HOA name")
    location: str = Field(..., description="HOA location/address")
    contact_email: Optional[str] = Field(None, description="HOA contact email")

# ===========================
# ✅ User Schemas
# ===========================

ValidRoles = Literal["admin", "hoa_board", "inspector"]

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username (3-20 chars, alphanumeric + underscore)")
    email: Optional[EmailStr] = Field(None, description="User email address")
    role: Optional[ValidRoles] = Field(default="inspector", description="User role in the system")
    hoa_id: Optional[int] = Field(None, description="Assigned HOA ID")

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
    hoa: Optional[HOAInfo] = Field(None, description="Assigned HOA information")

# ===========================
# ✅ Resident Schemas
# ===========================

class ResidentBase(BaseModel):
    name: str = Field(..., description="Resident name")
    address: str = Field(..., description="Property address/unit number")
    email: Optional[EmailStr] = Field(None, description="Resident email address")
    phone: Optional[str] = Field(None, description="Resident phone number")
    hoa_id: int = Field(..., description="HOA ID")
    notes: Optional[str] = Field(None, description="Additional notes about the resident")

class ResidentCreate(ResidentBase):
    pass

class ResidentOut(ResidentBase):
    id: int = Field(..., description="Unique resident identifier")
    violation_count: int = Field(default=0, description="Number of violations")
    class Config:
        orm_mode = True

# ===========================
# ✅ Violation Schemas
# ===========================

class ViolationBase(BaseModel):
    description: str = Field(..., description="Detailed violation description")
    summary: Optional[str] = Field(None, description="AI-generated summary of the violation")
    tags: Optional[str] = Field(None, description="Comma-separated violation tags")
    image_url: Optional[str] = Field(None, description="URL to violation image")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF report")
    hoa_id: Optional[int] = Field(None, description="HOA where violation occurred")
    user_id: Optional[int] = Field(None, description="User who inspected the violation")
    resident_id: Optional[int] = Field(None, description="Associated resident ID")

class ViolationCreate(ViolationBase):
    pass

class ViolationOut(BaseModel):
    id: int = Field(..., description="Unique violation identifier")
    violation_number: int = Field(..., description="Auto-increment violation number")
    timestamp: datetime = Field(..., description="When the violation was reported")
    description: str = Field(..., description="Detailed violation description")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    repeat_offender_score: Optional[int] = Field(default=1, description="Repeat offender score (1-5)")
    hoa_name: Optional[str] = Field(None, description="HOA name where violation occurred")
    address: Optional[str] = Field(None, description="Property address/unit number")
    location: Optional[str] = Field(None, description="Specific location within property")
    offender: Optional[str] = Field(None, description="Resident description")
    gps_coordinates: Optional[str] = Field(None, description="GPS coordinates")
    status: Optional[str] = Field(default="open", description="Violation status")
    pdf_path: Optional[str] = Field(None, description="Path to PDF report")
    image_url: Optional[str] = Field(None, description="Path to violation image")
    user_id: Optional[int] = Field(None, description="User who inspected the violation")
    inspected_by: Optional[str] = Field(None, description="Username of person who inspected")

    class Config:
        orm_mode = True

class ViolationList(BaseModel):
    violations: List[ViolationOut] = Field(..., description="List of violations")

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

class ViolationCreateRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed violation description")
    hoa: str = Field(..., description="HOA name in format 'HOA #XXX'")
    address: str = Field(..., min_length=2, max_length=100, description="Property address/unit number")
    location: str = Field(..., min_length=2, max_length=100, description="Specific location within property")
    offender: str = Field(..., min_length=2, max_length=100, description="Resident description")
    gps_coordinates: Optional[str] = Field(None, description="GPS coordinates")
    violation_type: Optional[str] = Field(None, description="Type of violation")

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

# ===========================
# ✅ Dispute Schemas
# ===========================

class DisputeCreate(BaseModel):
    violation_id: int
    reason: str
    evidence: Optional[str] = None
    evidence_file_path: Optional[str] = None
    contact_preference: Optional[str] = None

class DisputeOut(BaseModel):
    id: int
    violation_id: int
    resident_id: int
    reason: str
    evidence: Optional[str] = None
    evidence_file_path: Optional[str] = None
    contact_preference: Optional[str] = None
    status: str
    submitted_at: datetime

    class Config:
        orm_mode = True

# ===========================
# ✅ Communication & Notification Schemas
# ===========================

class CommunicationCreate(BaseModel):
    violation_id: int
    sender_id: int
    notification_type: str
    message: str
    recipients: str

class CommunicationOut(BaseModel):
    id: int
    violation_id: int
    sender_id: int
    notification_type: str
    message: str
    recipients: str
    sent_at: datetime
    status: str
    class Config:
        orm_mode = True

class NotificationOut(BaseModel):
    id: int
    communication_id: int
    recipient_email: str
    notification_type: str
    status: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    class Config:
        orm_mode = True


