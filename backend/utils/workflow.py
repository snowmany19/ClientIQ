# backend/utils/workflow.py

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models import Violation, User, Resident
from utils.logger import get_logger
from utils.email_alerts import send_violation_notification_email
from utils.pdf import generate_pdf

logger = get_logger("workflow")

def trigger_violation_workflow(violation: Violation, db: Session) -> None:
    """Trigger automated workflow for a new violation."""
    try:
        logger.info(f"Starting workflow for violation {violation.id}")
        
        # 1. Update resident violation count
        update_resident_violation_count(violation, db)
        
        # 2. Check for repeat offender escalation
        check_repeat_offender_escalation(violation, db)
        
        # 3. Schedule follow-up reminders
        schedule_follow_up_reminders(violation, db)
        
        # 4. Send initial notifications
        send_initial_notifications(violation, db)
        
        logger.info(f"Workflow completed for violation {violation.id}")
        
    except Exception as e:
        logger.error(f"Workflow failed for violation {violation.id}: {e}")

def update_resident_violation_count(violation: Violation, db: Session) -> None:
    """Update the violation count for the resident."""
    try:
        # Get violation data as strings
        address_str = getattr(violation, 'address', '') or ''
        offender_str = getattr(violation, 'offender', '') or ''
        
        # Find resident by address or offender name
        resident = find_resident(address_str, offender_str, db)
        if resident:
            # Use SQLAlchemy update to avoid type issues
            db.query(Resident).filter(Resident.id == resident.id).update(
                {"violation_count": Resident.violation_count + 1}
            )
            db.commit()
            logger.info(f"Updated violation count for resident {resident.id}")
    except Exception as e:
        logger.warning(f"Failed to update resident violation count: {e}")

def find_resident(address: str, offender: str, db: Session) -> Optional[Resident]:
    """Find resident by address or offender name."""
    try:
        # Try to find by address first
        resident = db.query(Resident).filter(
            Resident.address.ilike(f"%{address}%")
        ).first()
        
        if not resident:
            # Try to find by offender name
            resident = db.query(Resident).filter(
                Resident.name.ilike(f"%{offender}%")
            ).first()
        
        return resident
    except Exception as e:
        logger.warning(f"Failed to find resident: {e}")
        return None

def check_repeat_offender_escalation(violation: Violation, db: Session) -> None:
    """Check if violation requires escalation based on repeat offender score."""
    try:
        score = getattr(violation, 'repeat_offender_score', 1) or 1
        score_int = int(score) if score else 1
        
        if score_int >= 4:
            # Chronic violator - escalate to HOA board
            escalate_to_hoa_board(violation, db)
        elif score_int >= 3:
            # Pattern developing - send formal warning
            send_formal_warning(violation, db)
        elif score_int >= 2:
            # Second violation - send follow-up notice
            send_follow_up_notice(violation, db)
        
    except Exception as e:
        logger.warning(f"Failed to check repeat offender escalation: {e}")

def escalate_to_hoa_board(violation: Violation, db: Session) -> None:
    """Escalate violation to HOA board for review."""
    try:
        # Update violation status using SQLAlchemy update
        db.query(Violation).filter(Violation.id == violation.id).update(
            {"status": "under_review"}
        )
        db.commit()
        
        # Send notification to HOA board members
        hoa_name_str = getattr(violation, 'hoa_name', '') or ''
        hoa_board_members = get_hoa_board_members(hoa_name_str, db)
        for member in hoa_board_members:
            send_escalation_notification(member, violation)
        
        logger.info(f"Escalated violation {violation.id} to HOA board")
        
    except Exception as e:
        logger.warning(f"Failed to escalate to HOA board: {e}")

def send_formal_warning(violation: Violation, db: Session) -> None:
    """Send formal warning for pattern violations."""
    try:
        # Generate formal warning PDF
        warning_data = prepare_warning_data(violation)
        # warning_pdf = generate_pdf(warning_data, output_dir="static/warnings")
        
        # Send formal warning email
        send_formal_warning_email(violation)
        
        logger.info(f"Sent formal warning for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send formal warning: {e}")

def send_follow_up_notice(violation: Violation, db: Session) -> None:
    """Send follow-up notice for second violations."""
    try:
        # Send follow-up email
        send_follow_up_email(violation)
        
        logger.info(f"Sent follow-up notice for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send follow-up notice: {e}")

def schedule_follow_up_reminders(violation: Violation, db: Session) -> None:
    """Schedule automated follow-up reminders."""
    try:
        # Schedule reminders based on violation type and severity
        score = getattr(violation, 'repeat_offender_score', 1) or 1
        score_int = int(score) if score else 1
        reminder_days = get_reminder_schedule(score_int)
        
        for days in reminder_days:
            reminder_date = datetime.utcnow() + timedelta(days=days)
            schedule_reminder(violation, reminder_date)
        
        logger.info(f"Scheduled {len(reminder_days)} reminders for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to schedule reminders: {e}")

def get_reminder_schedule(score: int) -> List[int]:
    """Get reminder schedule based on violation type and severity."""
    if score >= 4:
        return [3, 7, 14]  # Chronic violator - frequent reminders
    elif score >= 3:
        return [7, 14]     # Pattern developing - moderate reminders
    elif score >= 2:
        return [14]        # Second violation - single reminder
    else:
        return [30]        # First violation - gentle reminder

def schedule_reminder(violation: Violation, reminder_date: datetime) -> None:
    """Schedule a reminder for a specific date."""
    try:
        # In a production system, this would use a task queue like Celery
        # For now, we'll log the reminder
        logger.info(f"Scheduled reminder for violation {violation.id} on {reminder_date}")
        
        # TODO: Implement actual scheduling with Celery or similar
        # celery_app.send_task('send_reminder', args=[violation.id, reminder_date])
        
    except Exception as e:
        logger.warning(f"Failed to schedule reminder: {e}")

def send_initial_notifications(violation: Violation, db: Session) -> None:
    """Send initial notifications for new violations."""
    try:
        # Send notification to HOA board
        hoa_name_str = getattr(violation, 'hoa_name', '') or ''
        hoa_board_members = get_hoa_board_members(hoa_name_str, db)
        for member in hoa_board_members:
            send_violation_notification(member, violation)
        
        logger.info(f"Sent initial notifications for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send initial notifications: {e}")

def get_hoa_board_members(hoa_name: str, db: Session) -> List[User]:
    """Get HOA board members for a specific HOA."""
    try:
        # Find HOA by name
        hoa_id = get_hoa_id_by_name(hoa_name)
        if hoa_id:
            return db.query(User).filter(
                User.hoa_id == hoa_id,
                User.role == "hoa_board"
            ).all()
        return []
    except Exception as e:
        logger.warning(f"Failed to get HOA board members: {e}")
        return []

def get_hoa_id_by_name(hoa_name: str) -> Optional[int]:
    """Get HOA ID by name."""
    try:
        # Extract HOA number from name (e.g., "HOA #001" -> 1)
        if hoa_name.startswith("HOA #"):
            hoa_number = hoa_name.split("#")[1]
            return int(hoa_number)
        return None
    except Exception as e:
        logger.warning(f"Failed to get HOA ID: {e}")
        return None

def send_violation_notification(user: User, violation: Violation) -> None:
    """Send violation notification to user."""
    try:
        subject = f"New Violation Report - {getattr(violation, 'hoa_name', 'Unknown HOA')}"
        body = f"""
        A new violation has been reported:
        
        Violation #: {getattr(violation, 'violation_number', 'N/A')}
        Address: {getattr(violation, 'address', 'N/A')}
        Location: {getattr(violation, 'location', 'N/A')}
        Resident: {getattr(violation, 'offender', 'N/A')}
        Description: {getattr(violation, 'description', 'N/A')}
        Repeat Offender Score: {getattr(violation, 'repeat_offender_score', 1)}
        
        Please review and take appropriate action.
        """
        
        # TODO: Implement email sending
        logger.info(f"Violation notification prepared for user {user.username}")
        
    except Exception as e:
        logger.warning(f"Failed to send violation notification: {e}")

def send_escalation_notification(user: User, violation: Violation) -> None:
    """Send escalation notification to HOA board member."""
    try:
        subject = f"URGENT: Violation Escalation - {getattr(violation, 'hoa_name', 'Unknown HOA')}"
        body = f"""
        A violation has been escalated for HOA board review:
        
        Violation #: {getattr(violation, 'violation_number', 'N/A')}
        Address: {getattr(violation, 'address', 'N/A')}
        Resident: {getattr(violation, 'offender', 'N/A')}
        Repeat Offender Score: {getattr(violation, 'repeat_offender_score', 1)}
        Status: {getattr(violation, 'status', 'unknown')}
        
        This violation requires immediate attention from the HOA board.
        """
        
        # TODO: Implement email sending
        logger.info(f"Escalation notification prepared for user {user.username}")
        
    except Exception as e:
        logger.warning(f"Failed to send escalation notification: {e}")

def send_formal_warning_email(violation: Violation) -> None:
    """Send formal warning email with PDF attachment."""
    try:
        subject = f"Formal Warning - {getattr(violation, 'hoa_name', 'Unknown HOA')}"
        body = f"""
        A formal warning has been issued for violation #{getattr(violation, 'violation_number', 'N/A')}.
        
        Please review the attached PDF for details and required corrective actions.
        
        This is a formal warning and may result in fines if not addressed promptly.
        """
        
        # TODO: Implement email with PDF attachment
        logger.info(f"Formal warning email prepared for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send formal warning email: {e}")

def send_follow_up_email(violation: Violation) -> None:
    """Send follow-up email for second violations."""
    try:
        subject = f"Follow-up Notice - {getattr(violation, 'hoa_name', 'Unknown HOA')}"
        body = f"""
        This is a follow-up notice for violation #{getattr(violation, 'violation_number', 'N/A')}.
        
        Address: {getattr(violation, 'address', 'N/A')}
        Resident: {getattr(violation, 'offender', 'N/A')}
        Description: {getattr(violation, 'description', 'N/A')}
        
        Please ensure this violation is addressed promptly to avoid further action.
        """
        
        # TODO: Implement email sending
        logger.info(f"Follow-up email prepared for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send follow-up email: {e}")

def prepare_warning_data(violation: Violation) -> Dict[str, Any]:
    """Prepare data for formal warning PDF."""
    return {
        "id": getattr(violation, 'id', 0),
        "violation_number": getattr(violation, 'violation_number', 0),
        "timestamp": getattr(violation, 'timestamp', datetime.utcnow()),
        "hoa": getattr(violation, 'hoa_name', 'Unknown HOA'),
        "address": getattr(violation, 'address', 'N/A'),
        "location": getattr(violation, 'location', 'N/A'),
        "offender": getattr(violation, 'offender', 'N/A'),
        "description": getattr(violation, 'description', 'N/A'),
        "summary": getattr(violation, 'summary', 'N/A'),
        "repeat_offender_score": getattr(violation, 'repeat_offender_score', 1),
        "status": "formal_warning",
        "username": "HOA Board",
        "tags": getattr(violation, 'tags', ''),
        "image_path": getattr(violation, 'image_url', ''),
        "gps_coordinates": getattr(violation, 'gps_coordinates', '')
    } 