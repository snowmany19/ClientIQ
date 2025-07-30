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
        
        # Send escalation notifications to HOA board members
        hoa_name_str = getattr(violation, 'hoa_name', '') or ''
        hoa_board_members = get_hoa_board_members(hoa_name_str, db)
        for member in hoa_board_members:
            send_escalation_notification(member, violation)
        
        logger.info(f"Escalated violation {violation.id} to HOA board")
        
    except Exception as e:
        logger.warning(f"Failed to escalate violation: {e}")

def send_formal_warning(violation: Violation, db: Session) -> None:
    """Send formal warning for repeat violations."""
    try:
        # Send formal warning email
        send_formal_warning_email(violation)
        
        # Update violation status
        db.query(Violation).filter(Violation.id == violation.id).update(
            {"status": "under_review"}
        )
        db.commit()
        
        logger.info(f"Sent formal warning for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send formal warning: {e}")

def send_follow_up_notice(violation: Violation, db: Session) -> None:
    """Send follow-up notice for second violation."""
    try:
        # Send follow-up email
        send_follow_up_email(violation)
        
        logger.info(f"Sent follow-up notice for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send follow-up notice: {e}")

def schedule_follow_up_reminders(violation: Violation, db: Session) -> None:
    """Schedule follow-up reminders based on repeat offender score."""
    try:
        score = getattr(violation, 'repeat_offender_score', 1) or 1
        score_int = int(score) if score else 1
        
        # Get reminder schedule based on score
        reminder_days = get_reminder_schedule(score_int)
        
        # Schedule reminders
        for days in reminder_days:
            reminder_date = datetime.utcnow() + timedelta(days=days)
            schedule_reminder(violation, reminder_date)
        
        logger.info(f"Scheduled {len(reminder_days)} reminders for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to schedule reminders: {e}")

def get_reminder_schedule(score: int) -> List[int]:
    """Get reminder schedule based on repeat offender score."""
    if score >= 4:
        return [7, 14, 30]  # Chronic violator - multiple reminders
    elif score >= 3:
        return [7, 21]       # Pattern developing - two reminders
    elif score >= 2:
        return [14]          # Second violation - one reminder
    else:
        return [30]        # First violation - gentle reminder

def schedule_reminder(violation: Violation, reminder_date: datetime) -> None:
    """Schedule a reminder for a specific date using Celery."""
    try:
        from utils.celery_tasks import celery_app
        
        # Schedule the reminder task
        celery_app.send_task(
            'utils.celery_tasks.send_reminder_notification',
            args=[violation.id, reminder_date.isoformat()],
            eta=reminder_date
        )
        
        logger.info(f"Scheduled reminder for violation {violation.id} on {reminder_date}")
        
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
        from utils.email_service import email_service
        
        if user.email:
            success = email_service.send_violation_notification(
                violation=violation,
                recipient_email=user.email,
                notification_type="initial"
            )
            if success:
                logger.info(f"Violation notification sent to user {user.username} at {user.email}")
            else:
                logger.warning(f"Failed to send violation notification to {user.email}")
        else:
            logger.warning(f"User {user.username} has no email address configured")
        
    except Exception as e:
        logger.warning(f"Failed to send violation notification: {e}")

def send_escalation_notification(user: User, violation: Violation) -> None:
    """Send escalation notification to HOA board member."""
    try:
        from utils.email_service import email_service
        
        if user.email:
            success = email_service.send_escalation_notification(
                violation=violation,
                recipient_email=user.email,
                escalation_reason="High repeat offender score or unresolved violation"
            )
            if success:
                logger.info(f"Escalation notification sent to user {user.username} at {user.email}")
            else:
                logger.warning(f"Failed to send escalation notification to {user.email}")
        else:
            logger.warning(f"User {user.username} has no email address configured")
        
    except Exception as e:
        logger.warning(f"Failed to send escalation notification: {e}")

def send_formal_warning_email(violation: Violation) -> None:
    """Send formal warning email with PDF attachment."""
    try:
        from utils.email_service import email_service
        
        # Get the PDF path if it exists
        pdf_path = getattr(violation, 'pdf_path', None)
        
        # Prepare warning data
        warning_data = prepare_warning_data(violation)
        
        # Send formal warning email
        success = email_service.send_formal_warning(
            violation=violation,
            recipient_email=warning_data.get('resident_email', ''),
            warning_data=warning_data,
            pdf_path=pdf_path
        )
        
        if success:
            logger.info(f"Formal warning email sent for violation {violation.id}")
        else:
            logger.warning(f"Failed to send formal warning email for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send formal warning email: {e}")

def send_follow_up_email(violation: Violation) -> None:
    """Send follow-up email for second violation."""
    try:
        from utils.email_service import email_service
        
        # Prepare follow-up data
        follow_up_data = prepare_warning_data(violation)
        
        # Send follow-up email
        success = email_service.send_follow_up_notice(
            violation=violation,
            recipient_email=follow_up_data.get('resident_email', ''),
            follow_up_data=follow_up_data
        )
        
        if success:
            logger.info(f"Follow-up email sent for violation {violation.id}")
        else:
            logger.warning(f"Failed to send follow-up email for violation {violation.id}")
        
    except Exception as e:
        logger.warning(f"Failed to send follow-up email: {e}")

def prepare_warning_data(violation: Violation) -> Dict[str, Any]:
    """Prepare warning data for email templates."""
    try:
        # Get resident information
        address_str = getattr(violation, 'address', '') or ''
        offender_str = getattr(violation, 'offender', '') or ''
        
        # Try to find resident
        from database import SessionLocal
        db = SessionLocal()
        resident = find_resident(address_str, offender_str, db)
        
        warning_data = {
            'violation_number': getattr(violation, 'violation_number', ''),
            'description': getattr(violation, 'description', ''),
            'address': address_str,
            'location': getattr(violation, 'location', ''),
            'timestamp': getattr(violation, 'timestamp', datetime.utcnow()).isoformat(),
            'repeat_offender_score': getattr(violation, 'repeat_offender_score', 1),
            'resident_name': getattr(resident, 'name', offender_str) if resident else offender_str,
            'resident_email': getattr(resident, 'email', '') if resident else '',
            'resident_phone': getattr(resident, 'phone', '') if resident else '',
            'hoa_name': getattr(violation, 'hoa_name', ''),
        }
        
        db.close()
        return warning_data
        
    except Exception as e:
        logger.warning(f"Failed to prepare warning data: {e}")
        return {} 