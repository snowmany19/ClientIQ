# models.py — SQLAlchemy models for ContractGuard.ai - AI Contract Review Platform

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from database to ensure all models use the same metadata
try:
    from database import Base
except ImportError:
    from backend.database import Base

# 🧑 User table with role-based access
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, nullable=True)
    first_name = Column(String, nullable=True)  # User's first name
    last_name = Column(String, nullable=True)   # User's last name
    company_name = Column(String, nullable=True)  # Company name
    phone = Column(String, nullable=True)       # User's phone number
    role = Column(String, default="analyst")  # admin | analyst | viewer | super_admin | resident | inspector
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)  # Workspace assignment
    
    # 💳 Billing fields
    stripe_customer_id = Column(String, nullable=True)  # Stripe customer ID
    subscription_id = Column(String, nullable=True)     # Stripe subscription ID
    plan_id = Column(String, default="basic")           # Current plan (basic, pro, enterprise)
    subscription_status = Column(String, default="inactive")  # active, inactive, cancelled, etc.
    trial_ends_at = Column(DateTime, nullable=True)     # Trial expiration
    billing_cycle_start = Column(DateTime, nullable=True)  # Current billing period start
    billing_cycle_end = Column(DateTime, nullable=True)    # Current billing period end
    
    # 🔐 Security fields
    two_factor_secret = Column(String, nullable=True)   # 2FA secret key
    two_factor_enabled = Column(Boolean, default=False) # 2FA status
    
    # ⚙️ User settings fields
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_contracts = Column(Boolean, default=True)
    notification_reports = Column(Boolean, default=True)
    theme_preference = Column(String, default="light")  # light, dark, auto
    pwa_offline_enabled = Column(Boolean, default=True)
    pwa_app_switcher_enabled = Column(Boolean, default=True)
    
    # 📅 Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)

    # Relationships
    contracts = relationship("ContractRecord", back_populates="owner", cascade="all, delete-orphan", foreign_keys="[ContractRecord.owner_user_id]")
    workspace = relationship("Workspace")  # Relationship to assigned workspace

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    device_info = Column(String, nullable=True)  # Browser, OS, device type
    ip_address = Column(String, nullable=True)
    location = Column(String, nullable=True)  # City, Country
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User")

# 🏢 Workspace table for multi-tenant support
class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    workspace_number = Column(String, unique=True, index=True)  # Auto-generated workspace number
    name = Column(String, index=True)
    company_name = Column(String, index=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)  # Company logo for PDF generation
    industry = Column(String, nullable=True)  # Legal, Tech, Finance, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="workspace")
    # contracts = relationship("ContractRecord", back_populates="workspace")  # Commented out since ContractRecord no longer has workspace relationship

# 📄 Contract Record table for AI contract analysis
class ContractRecord(Base):
    __tablename__ = "contract_records"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)  # Removed since column doesn't exist in DB
    title = Column(String, nullable=False, index=True)
    counterparty = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # NDA, MSA, SOW, Employment, Vendor, Lease, Other
    effective_date = Column(DateTime, nullable=True)
    term_end = Column(DateTime, nullable=True)
    renewal_terms = Column(Text, nullable=True)
    governing_law = Column(String, nullable=True)
    uploaded_files = Column(JSON, default=list)  # Array of file paths
    analysis_json = Column(JSON, nullable=True)  # AI analysis results
    summary_text = Column(Text, nullable=True)
    risk_items = Column(JSON, default=list)  # Array of risk assessments
    rewrite_suggestions = Column(JSON, default=list)  # Array of suggestions
    status = Column(String, default="pending")  # pending, analyzed, reviewed, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="contracts", foreign_keys=[owner_user_id])
    # workspace = relationship("Workspace", back_populates="contracts")  # Commented out since workspace_id column doesn't exist

# 📊 Analytics Event table for tracking user actions
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    event_type = Column(String, nullable=False)  # contract_upload, contract_analysis, user_login, etc.
    event_data = Column(JSON, nullable=True)  # Additional event data
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace")

# 🔐 Two-Factor Authentication table
class TwoFactorCode(Base):
    __tablename__ = "two_factor_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

# 📧 Email Template table for customizable email communications
class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # Available template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 💾 File Storage table for managing uploaded documents
class FileStorage(Base):
    __tablename__ = "file_storage"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contract_records.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace")
    contract = relationship("ContractRecord")

# 📋 Communication Log table for tracking all communications
class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contract_records.id"), nullable=True)
    communication_type = Column(String, nullable=False)  # email, notification, report, etc.
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    recipient_email = Column(String, nullable=True)
    status = Column(String, default="sent")  # sent, delivered, failed, read
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    workspace = relationship("Workspace")
    user = relationship("User")
    contract = relationship("ContractRecord")

# 🔔 Notification table for user notifications
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contract_records.id"), nullable=True)
    notification_type = Column(String, nullable=False)  # contract_analysis, risk_alert, system, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace")
    contract = relationship("ContractRecord")

# 📊 Performance Metrics table for system monitoring
class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)  # ms, MB, count, etc.
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_context = Column(JSON, nullable=True)  # Additional context

    # Relationships
    workspace = relationship("Workspace")
    user = relationship("User")



