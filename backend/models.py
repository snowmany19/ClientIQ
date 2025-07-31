# models.py — SQLAlchemy models for the CivicLogHOA - HOA Violation Management system

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from database to ensure all models use the same metadata
try:
    from database import Base
except ImportError:
    from backend.database import Base

# 📝 Violation table
class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    violation_number = Column(Integer, unique=True, index=True, nullable=True)  # Unique violation number, set after creation
    description = Column(Text)                   # Raw violation report
    summary = Column(Text)                       # GPT summary
    tags = Column(String)                        # Comma-separated tags
    timestamp = Column(DateTime, default=datetime.utcnow)

    hoa_name = Column(String)                    # HOA name (text)
    address = Column(String)                     # Property address/unit number
    location = Column(String)                    # Specific location within property
    offender = Column(String)                    # Resident name/description

    # New HOA-specific fields
    gps_coordinates = Column(String, nullable=True)  # GPS coordinates for mobile capture
    status = Column(String, default="open")      # open, under_review, resolved, disputed
    repeat_offender_score = Column(Integer, default=1)  # Renamed from severity

    # Resolution tracking fields
    resolved_at = Column(DateTime, nullable=True)      # When violation was resolved
    resolved_by = Column(String, nullable=True)        # Who resolved the violation
    resolution_notes = Column(Text, nullable=True)     # Notes about resolution
    reviewed_at = Column(DateTime, nullable=True)      # When violation was reviewed
    reviewed_by = Column(String, nullable=True)        # Who reviewed the violation

    image_url = Column(String, nullable=True)    # Optional image path
    pdf_path = Column(String, nullable=True)

    # Letter tracking fields
    letter_generated_at = Column(DateTime, nullable=True)
    letter_sent_at = Column(DateTime, nullable=True)
    letter_content = Column(Text, nullable=True)
    letter_recipient_email = Column(String, nullable=True)
    letter_status = Column(String, default="not_sent")  # not_sent, sent, delivered, opened
    letter_sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 🔗 FK to inspector
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="violations", foreign_keys=[user_id])
    letter_sender = relationship("User", foreign_keys=[letter_sent_by])

# 🧑 User table with role-based access
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, nullable=True)
    first_name = Column(String, nullable=True)  # User's first name
    last_name = Column(String, nullable=True)   # User's last name
    company_name = Column(String, nullable=True)  # Company or HOA name
    phone = Column(String, nullable=True)       # User's phone number
    role = Column(String, default="inspector")  # inspector | hoa_board | admin | resident
    hoa_id = Column(Integer, ForeignKey("hoas.id"), nullable=True)  # HOA assignment (renamed from store_id)
    
    # 💳 Billing fields
    stripe_customer_id = Column(String, nullable=True)  # Stripe customer ID
    subscription_id = Column(String, nullable=True)     # Stripe subscription ID
    plan_id = Column(String, default="basic")           # Current plan (basic, pro, enterprise)
    subscription_status = Column(String, default="inactive")  # active, past_due, canceled, etc.
    trial_ends_at = Column(DateTime, nullable=True)     # Trial expiration
    billing_cycle_start = Column(DateTime, nullable=True)  # Current billing period start
    billing_cycle_end = Column(DateTime, nullable=True)    # Current billing period end
    
    # 🔐 Security fields
    two_factor_secret = Column(String, nullable=True)   # 2FA secret key
    two_factor_enabled = Column(Boolean, default=False) # 2FA status
    
    # ⚙️ User settings fields
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_violations = Column(Boolean, default=True)
    notification_reports = Column(Boolean, default=True)
    theme_preference = Column(String, default="light")  # light, dark, auto
    pwa_offline_enabled = Column(Boolean, default=True)
    pwa_app_switcher_enabled = Column(Boolean, default=True)
    
    # 📅 Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)

    violations = relationship("Violation", back_populates="user", cascade="all, delete-orphan", foreign_keys="[Violation.user_id]")
    hoa = relationship("HOA")  # Relationship to assigned HOA

# 📱 User Session table for session management
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

# 🏘️ HOA table (renamed from Store)
class HOA(Base):
    __tablename__ = "hoas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)  # HOA logo for PDF generation

# 🧑‍🚨 Resident table (renamed from Offender)
class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hoa_id = Column(Integer, ForeignKey("hoas.id"))
    notes = Column(Text)
    violation_count = Column(Integer, default=0)  # Track repeat violations

    hoa = relationship("HOA")

# 📝 Dispute table (for resident violation disputes)
class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"), nullable=False)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    reason = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    evidence_file_path = Column(String, nullable=True)
    contact_preference = Column(String, nullable=True)
    status = Column(String, default="pending")
    submitted_at = Column(DateTime, default=datetime.utcnow)

    violation = relationship("Violation")
    resident = relationship("Resident")

# 📧 Violation Letter table for tracking letter delivery
class ViolationLetter(Base):
    __tablename__ = "violation_letters"

    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"), nullable=False)
    letter_content = Column(Text, nullable=False)
    recipient_email = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="sent")  # sent, delivered, opened, clicked, failed
    email_message_id = Column(String, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    violation = relationship("Violation")
    sender = relationship("User")

# 📞 Communication table for tracking all communications
class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String, nullable=False)  # initial, warning, escalation, resolution
    message = Column(Text, nullable=False)
    recipients = Column(String, nullable=False)  # Comma-separated emails
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="sent")

    violation = relationship("Violation")
    sender = relationship("User")

# 🔔 Notification table for tracking individual notifications
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey("communications.id"), nullable=False)
    recipient_email = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    status = Column(String, default="sent")  # sent, delivered, read, failed
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    communication = relationship("Communication")



