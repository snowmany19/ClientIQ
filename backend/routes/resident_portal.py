# backend/routes/resident_portal.py

from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import Violation, User, Resident, Dispute
from schemas import ViolationOut, DisputeCreate, DisputeOut
from utils.auth_utils import get_current_user, require_active_subscription
from utils.logger import get_logger
from utils.email_alerts import send_email_alert

router = APIRouter(prefix="/resident-portal", tags=["Resident Portal"])
logger = get_logger("resident_portal")

@router.get("/my-violations", response_model=List[ViolationOut])
def get_my_violations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get violations for the current resident."""
    try:
        # Find resident by user ID or email
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get violations for this resident
        violations = db.query(Violation).filter(
            (Violation.address.ilike(f"%{resident.address}%")) |
            (Violation.offender.ilike(f"%{resident.name}%"))
        ).order_by(Violation.timestamp.desc()).all()
        
        return violations
        
    except Exception as e:
        logger.error(f"Failed to get resident violations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve violations"
        )

@router.get("/violation/{violation_id}", response_model=ViolationOut)
def get_violation_details(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get detailed information about a specific violation."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Check if resident owns this violation
        if not (
            violation.address and resident.address and 
            violation.address.lower() in resident.address.lower()
        ) and not (
            violation.offender and resident.name and
            violation.offender.lower() in resident.name.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this violation"
            )
        
        return violation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get violation details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve violation details"
        )

@router.post("/dispute", response_model=DisputeOut)
def submit_dispute(
    violation_id: int = Form(...),
    reason: str = Form(...),
    evidence: str = Form(...),
    contact_preference: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Submit a dispute for a violation."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Check if resident owns this violation
        if not (
            violation.address and resident.address and 
            violation.address.lower() in resident.address.lower()
        ) and not (
            violation.offender and resident.name and
            violation.offender.lower() in resident.name.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this violation"
            )
        
        # Check if dispute already exists
        existing_dispute = db.query(Dispute).filter(
            Dispute.violation_id == violation_id,
            Dispute.resident_id == resident.id
        ).first()
        
        if existing_dispute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dispute already submitted for this violation"
            )
        
        # Save evidence file if provided
        evidence_file_path = None
        if file:
            evidence_file_path = save_evidence_file(file, violation_id, resident.id)
        
        # Create dispute
        dispute = Dispute(
            violation_id=violation_id,
            resident_id=resident.id,
            reason=reason,
            evidence=evidence,
            evidence_file_path=evidence_file_path,
            contact_preference=contact_preference,
            status="pending",
            submitted_at=datetime.utcnow()
        )
        
        db.add(dispute)
        db.commit()
        db.refresh(dispute)
        
        # Update violation status
        db.query(Violation).filter(Violation.id == violation_id).update(
            {"status": "disputed"}
        )
        db.commit()
        
        # Send notification to HOA board
        send_dispute_notification(dispute, violation, resident, db)
        
        logger.info(f"Dispute submitted for violation {violation_id} by resident {resident.id}")
        
        return dispute
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit dispute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit dispute"
        )

@router.get("/my-disputes", response_model=List[DisputeOut])
def get_my_disputes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get disputes submitted by the current resident."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get disputes
        disputes = db.query(Dispute).filter(
            Dispute.resident_id == resident.id
        ).order_by(Dispute.submitted_at.desc()).all()
        
        return disputes
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resident disputes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve disputes"
        )

@router.get("/dispute/{dispute_id}", response_model=DisputeOut)
def get_dispute_details(
    dispute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get detailed information about a specific dispute."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get dispute
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
        
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found"
            )
        
        # Check if resident owns this dispute
        if dispute.resident_id != resident.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this dispute"
            )
        
        return dispute
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dispute details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dispute details"
        )

@router.post("/contact-hoa")
def contact_hoa(
    subject: str = Form(...),
    message: str = Form(...),
    violation_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Send a message to the HOA board."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get HOA board members
        hoa_board_members = db.query(User).filter(
            User.role == "hoa_board",
            User.hoa_id == resident.hoa_id
        ).all()
        
        if not hoa_board_members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HOA board members not found"
            )
        
        # Send message to all HOA board members
        for member in hoa_board_members:
            send_hoa_contact_message(member, resident, subject, message, violation_id)
        
        logger.info(f"Contact message sent to HOA board by resident {resident.id}")
        
        return {"message": "Message sent successfully to HOA board"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send contact message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )

@router.get("/profile")
def get_resident_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get the current resident's profile information."""
    try:
        # Find resident
        resident = db.query(Resident).filter(
            (Resident.user_id == current_user.id) |
            (Resident.email == current_user.email)
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get violation statistics
        violations = db.query(Violation).filter(
            (Violation.address.ilike(f"%{resident.address}%")) |
            (Violation.offender.ilike(f"%{resident.name}%"))
        ).all()
        
        stats = {
            "total_violations": len(violations),
            "open_violations": len([v for v in violations if v.status == "open"]),
            "resolved_violations": len([v for v in violations if v.status == "resolved"]),
            "disputed_violations": len([v for v in violations if v.status == "disputed"]),
            "average_repeat_offender_score": sum(v.repeat_offender_score or 1 for v in violations) / len(violations) if violations else 0
        }
        
        return {
            "resident": {
                "id": resident.id,
                "name": resident.name,
                "address": resident.address,
                "email": resident.email,
                "phone": resident.phone,
                "violation_count": resident.violation_count
            },
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resident profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

def save_evidence_file(file: UploadFile, violation_id: int, resident_id: int) -> Optional[str]:
    """Save evidence file for dispute."""
    try:
        import os
        from uuid import uuid4
        
        # Create evidence directory
        evidence_dir = "static/evidence"
        os.makedirs(evidence_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
        filename = f"evidence_v{violation_id}_r{resident_id}_{timestamp}_{unique_id}{file_extension}"
        file_path = os.path.join(evidence_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save evidence file: {e}")
        return None

def send_dispute_notification(dispute: Dispute, violation: Violation, resident: Resident, db: Session) -> None:
    """Send notification to HOA board about new dispute."""
    try:
        # Get HOA board members
        hoa_board_members = db.query(User).filter(
            User.role == "hoa_board",
            User.hoa_id == resident.hoa_id
        ).all()
        
        for member in hoa_board_members:
            subject = f"New Dispute Filed - Violation #{violation.violation_number}"
            body = f"""
            A new dispute has been filed:
            
            Violation #: {violation.violation_number}
            Resident: {resident.name}
            Address: {resident.address}
            Reason: {dispute.reason}
            Contact Preference: {dispute.contact_preference}
            
            Please review and respond accordingly.
            """
            
            # TODO: Implement email sending
            logger.info(f"Dispute notification prepared for HOA board member {member.username}")
            
    except Exception as e:
        logger.warning(f"Failed to send dispute notification: {e}")

def send_hoa_contact_message(member: User, resident: Resident, subject: str, message: str, violation_id: Optional[int]) -> None:
    """Send contact message to HOA board member."""
    try:
        email_subject = f"Resident Contact: {subject}"
        email_body = f"""
        Message from resident {resident.name} ({resident.address}):
        
        Subject: {subject}
        Message: {message}
        """
        
        if violation_id:
            email_body += f"\nRelated to Violation #{violation_id}"
        
        email_body += f"""
        
        Contact Information:
        Email: {resident.email}
        Phone: {resident.phone}
        """
        
        # TODO: Implement email sending
        logger.info(f"Contact message prepared for HOA board member {member.username}")
        
    except Exception as e:
        logger.warning(f"Failed to send contact message: {e}") 