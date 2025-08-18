# schemas.py
# ✅ Pydantic schemas for ContractGuard.ai - AI Contract Review Platform

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

# ===========================
# ✅ Workspace Schemas
# ===========================

class WorkspaceBase(BaseModel):
    name: str = Field(..., description="Workspace name")
    company_name: str = Field(..., description="Company name")
    contact_email: Optional[str] = Field(None, description="Company contact email")
    contact_phone: Optional[str] = Field(None, description="Company contact phone")
    logo_url: Optional[str] = Field(None, description="Company logo URL")
    industry: Optional[str] = Field(None, description="Industry type (Legal, Tech, Finance, etc.)")

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceOut(WorkspaceBase):
    id: int = Field(..., description="Unique workspace identifier")
    workspace_number: str = Field(..., description="Auto-generated workspace number")
    created_at: datetime = Field(..., description="Workspace creation date")
    updated_at: datetime = Field(..., description="Workspace last update date")
    
    class Config:
        from_attributes = True

class WorkspaceInfo(BaseModel):
    id: int = Field(..., description="Unique workspace identifier")
    workspace_number: str = Field(..., description="Workspace number")
    name: str = Field(..., description="Workspace name")
    company_name: str = Field(..., description="Company name")
    contact_email: Optional[str] = Field(None, description="Company contact email")
    industry: Optional[str] = Field(None, description="Industry type")

# ===========================
# ✅ User Schemas
# ===========================

ValidRoles = Literal["admin", "analyst", "viewer", "super_admin"]

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username (3-20 chars, alphanumeric + underscore)")
    email: Optional[EmailStr] = Field(None, description="User email address")
    role: Optional[ValidRoles] = Field(default="analyst", description="User role in the system")
    workspace_id: Optional[int] = Field(None, description="Assigned workspace ID")

class UserCreate(UserBase):
    password: str = Field(..., description="User password (min 8 chars)")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="User's phone number")

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, description="User password (min 8 chars if provided)")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="User's phone number")

class UserOut(UserBase):
    id: int = Field(..., description="Unique user identifier")
    subscription_status: str = Field(default="inactive", description="Current subscription status")
    plan_id: str = Field(default="basic", description="Current plan")
    
    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User username")
    email: Optional[EmailStr] = Field(None, description="User email address")
    role: ValidRoles = Field(..., description="User role")
    subscription_status: Optional[str] = Field(default="inactive", description="Current subscription status")
    plan_id: Optional[str] = Field(default="basic", description="Current plan")
    workspace: Optional[WorkspaceInfo] = Field(None, description="Assigned workspace information")

# ===========================
# ✅ Contract Schemas
# ===========================

ValidContractCategories = Literal["NDA", "MSA", "SOW", "Employment", "Vendor", "Lease", "Other"]

class ContractRisk(BaseModel):
    severity: int = Field(..., ge=1, le=5, description="Risk severity (1-5)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0-1.0)")
    category: str = Field(..., description="Risk category")
    title: str = Field(..., description="Risk title")
    description: str = Field(..., description="Risk description")
    rationale: str = Field(..., description="Risk rationale")
    clause_reference: Optional[str] = Field(None, description="Reference to specific clause")
    business_impact: str = Field(..., description="Business impact description")
    mitigation_suggestions: List[str] = Field(default_factory=list, description="Mitigation suggestions")

class ContractSuggestion(BaseModel):
    risk_id: str = Field(..., description="Associated risk ID")
    type: Literal["balanced", "company_favorable"] = Field(..., description="Suggestion type")
    category: str = Field(..., description="Suggestion category")
    original_text: Optional[str] = Field(None, description="Original contract text")
    suggested_text: str = Field(..., description="Suggested replacement text")
    rationale: str = Field(..., description="Suggestion rationale")
    negotiation_tips: List[str] = Field(default_factory=list, description="Negotiation tips")
    fallback_position: Optional[str] = Field(None, description="Fallback negotiation position")

class ContractRecordBase(BaseModel):
    title: str = Field(..., description="Contract title")
    counterparty: str = Field(..., description="Contract counterparty/other party")
    category: ValidContractCategories = Field(..., description="Contract category")
    effective_date: Optional[datetime] = Field(None, description="Contract effective date")
    term_end: Optional[datetime] = Field(None, description="Contract end date")
    renewal_terms: Optional[str] = Field(None, description="Renewal terms")
    governing_law: Optional[str] = Field(None, description="Governing law")
    uploaded_files: List[str] = Field(default_factory=list, description="List of uploaded file paths")
    status: str = Field(default="pending", description="Contract status")

class ContractRecordCreate(ContractRecordBase):
    pass

class ContractRecordUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Contract title")
    counterparty: Optional[str] = Field(None, description="Contract counterparty")
    category: Optional[ValidContractCategories] = Field(None, description="Contract category")
    effective_date: Optional[datetime] = Field(None, description="Contract effective date")
    term_end: Optional[datetime] = Field(None, description="Contract end date")
    renewal_terms: Optional[str] = Field(None, description="Renewal terms")
    governing_law: Optional[str] = Field(None, description="Governing law")
    status: Optional[str] = Field(None, description="Contract status")

class ContractRecordOut(ContractRecordBase):
    id: int = Field(..., description="Unique contract identifier")
    owner_user_id: int = Field(..., description="Contract owner user ID")
    # workspace_id: int = Field(..., description="Contract workspace ID")  # Removed since column doesn't exist in DB
    analysis_json: Optional[dict] = Field(None, description="AI analysis results")
    summary_text: Optional[str] = Field(None, description="AI-generated summary")
    risk_items: List[ContractRisk] = Field(default_factory=list, description="Risk assessment items")
    rewrite_suggestions: List[ContractSuggestion] = Field(default_factory=list, description="Rewrite suggestions")
    created_at: datetime = Field(..., description="Contract creation date")
    updated_at: datetime = Field(..., description="Contract last update date")
    owner_username: Optional[str] = Field(None, description="Contract owner username")

    class Config:
        from_attributes = True

class ContractRecordList(BaseModel):
    contracts: List[ContractRecordOut] = Field(..., description="List of contracts")
    total: int = Field(..., description="Total number of contracts")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")

# ===========================
# ✅ Authentication Schemas
# ===========================

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username from token")
    role: Optional[ValidRoles] = Field(None, description="User role from token")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")
    user: UserInfo = Field(..., description="User information")

# ===========================
# ✅ Billing Schemas
# ===========================

class SubscriptionPlan(BaseModel):
    id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Plan name")
    price: float = Field(..., description="Plan price")
    currency: str = Field(default="USD", description="Currency")
    interval: str = Field(..., description="Billing interval")
    features: List[str] = Field(default_factory=list, description="Plan features")
    limits: dict = Field(..., description="Plan limits")

class UserSubscription(BaseModel):
    subscription_id: str = Field(..., description="Stripe subscription ID")
    plan_id: str = Field(..., description="Plan identifier")
    status: str = Field(..., description="Subscription status")
    current_period_start: str = Field(..., description="Current period start")
    current_period_end: str = Field(..., description="Current period end")
    cancel_at_period_end: bool = Field(..., description="Cancel at period end flag")
    features: List[str] = Field(default_factory=list, description="Subscription features")
    limits: dict = Field(..., description="Subscription limits")

# ===========================
# ✅ Analytics Schemas
# ===========================

class DashboardMetrics(BaseModel):
    # Contract metrics
    total_contracts: int = Field(..., description="Total contracts")
    analyzed_contracts: int = Field(..., description="Analyzed contracts")
    pending_contracts: int = Field(..., description="Pending contracts")
    high_risk_contracts: int = Field(..., description="High risk contracts")
    monthly_contract_trends: List[dict] = Field(default_factory=list, description="Monthly trends")
    top_contract_categories: List[dict] = Field(default_factory=list, description="Top categories")
    average_analysis_time: float = Field(..., description="Average analysis time")

# ===========================
# ✅ Utility Schemas
# ===========================

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
# ✅ Contract Analysis Schemas
# ===========================

class ContractAnalysisRequest(BaseModel):
    contract_id: int = Field(..., description="Contract ID to analyze")

class ContractAnalysisResponse(BaseModel):
    contract_id: int = Field(..., description="Contract ID")
    summary: str = Field(..., description="AI-generated summary")
    risks: List[ContractRisk] = Field(..., description="Risk assessment items")
    suggestions: List[ContractSuggestion] = Field(..., description="Rewrite suggestions")
    analysis_completed: bool = Field(..., description="Analysis completion status")

# ===========================
# ✅ File Upload Schemas
# ===========================

class FileUploadResponse(BaseModel):
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="File storage path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="File MIME type")
    contract_id: Optional[int] = Field(None, description="Associated contract ID")


