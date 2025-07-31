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
from utils.email_alerts import send_violation_notification_email

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
        # Find resident by email (since Resident doesn't have user_id)
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
        ).first()
        
        if not resident:
            # Return empty list if no resident profile found
            logger.warning(f"No resident profile found for user {current_user.email}")
            return []
        
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
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
                detail="Dispute already exists for this violation"
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
            status="pending"
        )
        
        db.add(dispute)
        db.commit()
        db.refresh(dispute)
        
        # Update violation status
        violation.status = "disputed"
        db.commit()
        
        # Send notification
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
    """Get disputes for the current resident."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get disputes for this resident
        disputes = db.query(Dispute).filter(
            Dispute.resident_id == resident.id
        ).order_by(Dispute.submitted_at.desc()).all()
        
        return disputes
        
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
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
    """Contact HOA board members."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get HOA board members
        hoa_members = db.query(User).filter(
            User.hoa_id == resident.hoa_id,
            User.role.in_(["hoa_board", "admin"])
        ).all()
        
        if not hoa_members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No HOA board members found"
            )
        
        # Send message to all board members
        for member in hoa_members:
            if member.email:
                send_hoa_contact_message(member, resident, subject, message, violation_id)
        
        logger.info(f"HOA contact message sent by resident {resident.id} to {len(hoa_members)} board members")
        return {"message": "Message sent to HOA board members"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send HOA contact message: {e}")
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
    """Get resident profile information."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
        ).first()
        
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident profile not found"
            )
        
        # Get violation count
        violation_count = db.query(Violation).filter(
            (Violation.address.ilike(f"%{resident.address}%")) |
            (Violation.offender.ilike(f"%{resident.name}%"))
        ).count()
        
        # Get dispute count
        dispute_count = db.query(Dispute).filter(
            Dispute.resident_id == resident.id
        ).count()
        
        return {
            "resident": {
                "id": resident.id,
                "name": resident.name,
                "address": resident.address,
                "email": resident.email,
                "phone": resident.phone,
                "notes": resident.notes,
                "violation_count": violation_count,
                "dispute_count": dispute_count
            },
            "user": {
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone": current_user.phone
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resident profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

# Helper functions

def save_evidence_file(file: UploadFile, violation_id: int, resident_id: int) -> Optional[str]:
    """Save evidence file and return the file path."""
    try:
        # Create directory if it doesn't exist
        import os
        evidence_dir = f"static/evidence/violation_{violation_id}"
        os.makedirs(evidence_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evidence_{resident_id}_{timestamp}_{file.filename}"
        file_path = f"{evidence_dir}/{filename}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save evidence file: {e}")
        return None

def send_dispute_notification(dispute: Dispute, violation: Violation, resident: Resident, db: Session) -> None:
    """Send dispute notification to HOA board members."""
    try:
        from utils.email_service import email_service
        
        # Get HOA board members
        hoa_members = db.query(User).filter(
            User.hoa_id == resident.hoa_id,
            User.role.in_(["hoa_board", "admin"])
        ).all()
        
        for member in hoa_members:
            if member.email:
                success = email_service.send_dispute_notification(
                    dispute=dispute,
                    violation=violation,
                    resident=resident,
                    recipient_email=member.email
                )
                if success:
                    logger.info(f"Dispute notification sent to {member.email}")
                else:
                    logger.warning(f"Failed to send dispute notification to {member.email}")
                    
    except Exception as e:
        logger.error(f"Failed to send dispute notification: {e}")

def send_hoa_contact_message(member: User, resident: Resident, subject: str, message: str, violation_id: Optional[int]) -> None:
    """Send HOA contact message."""
    try:
        from utils.email_service import email_service
        
        if member.email:
            success = email_service.send_email(
                to_email=member.email,
                subject=f"HOA Contact: {subject}",
                body=f"""
                Message from resident {resident.name} ({resident.email}):
                
                {message}
                
                Resident Address: {resident.address}
                {f'Related Violation ID: {violation_id}' if violation_id else ''}
                """,
                html_body=f"""
                <h3>Message from resident {resident.name}</h3>
                <p><strong>From:</strong> {resident.email}</p>
                <p><strong>Address:</strong> {resident.address}</p>
                {f'<p><strong>Related Violation ID:</strong> {violation_id}</p>' if violation_id else ''}
                <hr>
                <p>{message.replace(chr(10), '<br>')}</p>
                """
            )
            if success:
                logger.info(f"HOA contact message sent to {member.email}")
            else:
                logger.warning(f"Failed to send HOA contact message to {member.email}")
                
    except Exception as e:
        logger.error(f"Failed to send HOA contact message: {e}") 

@router.get("/violation/{violation_id}/letter")
def get_violation_letter(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get violation letter for resident viewing."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
        
        # Get letter information
        from models import ViolationLetter
        letters = db.query(ViolationLetter).filter(
            ViolationLetter.violation_id == violation_id,
            ViolationLetter.recipient_email == current_user.email
        ).order_by(ViolationLetter.sent_at.desc()).all()
        
        return {
            "violation_id": violation.id,
            "violation_number": violation.violation_number,
            "letter_content": violation.letter_content,
            "letter_generated_at": violation.letter_generated_at,
            "letter_sent_at": violation.letter_sent_at,
            "letter_status": violation.letter_status,
            "letters_sent": [
                {
                    "id": letter.id,
                    "sent_at": letter.sent_at,
                    "status": letter.status,
                    "opened_at": letter.opened_at
                }
                for letter in letters
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get violation letter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve violation letter"
        )

@router.get("/my-letters")
def get_my_letters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get all letters sent to the current resident."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
        ).all()
        
        violation_ids = [v.id for v in violations]
        
        # Get letters for these violations
        from models import ViolationLetter
        letters = db.query(ViolationLetter).filter(
            ViolationLetter.violation_id.in_(violation_ids),
            ViolationLetter.recipient_email == current_user.email
        ).order_by(ViolationLetter.sent_at.desc()).all()
        
        # Get violation details for each letter
        result = []
        for letter in letters:
            violation = next((v for v in violations if v.id == letter.violation_id), None)
            if violation:
                result.append({
                    "letter_id": letter.id,
                    "violation_id": violation.id,
                    "violation_number": violation.violation_number,
                    "description": violation.description,
                    "address": violation.address,
                    "sent_at": letter.sent_at,
                    "status": letter.status,
                    "opened_at": letter.opened_at,
                    "letter_content": letter.letter_content
                })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resident letters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve letters"
        )

@router.post("/violation/{violation_id}/mark-letter-read")
def mark_letter_as_read(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Mark a violation letter as read by the resident."""
    try:
        # Find resident by email
        resident = db.query(Resident).filter(
            Resident.email == current_user.email
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
        
        # Update letter status
        from models import ViolationLetter
        letter = db.query(ViolationLetter).filter(
            ViolationLetter.violation_id == violation_id,
            ViolationLetter.recipient_email == current_user.email
        ).order_by(ViolationLetter.sent_at.desc()).first()
        
        if letter:
            letter.opened_at = datetime.utcnow()
            letter.status = "opened"
            db.commit()
            
            logger.info(f"Letter marked as read by resident {current_user.email} for violation {violation_id}")
            return {"status": "success", "message": "Letter marked as read"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Letter not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark letter as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark letter as read"
        ) 