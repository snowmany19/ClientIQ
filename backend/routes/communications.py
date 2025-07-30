# backend/routes/communications.py

from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from database import get_db
from models import Violation, User, Resident, Communication, Notification
from schemas import CommunicationCreate, CommunicationOut, NotificationOut
from utils.auth_utils import get_current_user, require_active_subscription
from utils.logger import get_logger
from utils.email_alerts import send_violation_notification_email

router = APIRouter(prefix="/communications", tags=["Communications"])
logger = get_logger("communications")

@router.post("/send-notification", response_model=CommunicationOut)
def send_notification(
    violation_id: int = Form(...),
    notification_type: str = Form(...),  # initial, warning, escalation, resolution
    message: str = Form(...),
    recipients: List[str] = Form(...),  # List of recipient emails
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Send a notification for a violation."""
    try:
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Create communication record
        communication = Communication(
            violation_id=violation_id,
            sender_id=current_user.id,
            notification_type=notification_type,
            message=message,
            recipients=",".join(recipients),
            sent_at=datetime.utcnow(),
            status="sent"
        )
        
        db.add(communication)
        db.commit()
        db.refresh(communication)
        
        # Send emails to recipients
        for recipient_email in recipients:
            send_violation_notification_email(
                recipient_email, violation, notification_type, message, current_user
            )
        
        # Create notification records for tracking
        for recipient_email in recipients:
            notification = Notification(
                communication_id=communication.id,
                recipient_email=recipient_email,
                notification_type=notification_type,
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(notification)
        
        db.commit()
        
        logger.info(f"Notification sent for violation {violation_id} to {len(recipients)} recipients")
        
        return communication
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )

@router.post("/bulk-notify")
def bulk_notify(
    violation_ids: List[int] = Form(...),
    notification_type: str = Form(...),
    message_template: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Send bulk notifications for multiple violations."""
    try:
        results = []
        
        for violation_id in violation_ids:
            try:
                # Get violation
                violation = db.query(Violation).filter(Violation.id == violation_id).first()
                if not violation:
                    results.append({
                        "violation_id": violation_id,
                        "status": "failed",
                        "error": "Violation not found"
                    })
                    continue
                
                # Get recipient (resident)
                resident = get_resident_for_violation(violation, db)
                if not resident or not resident.email:
                    results.append({
                        "violation_id": violation_id,
                        "status": "failed",
                        "error": "No resident email found"
                    })
                    continue
                
                # Customize message
                customized_message = customize_message(message_template, violation, resident)
                
                # Create communication record
                communication = Communication(
                    violation_id=violation_id,
                    sender_id=current_user.id,
                    notification_type=notification_type,
                    message=customized_message,
                    recipients=resident.email,
                    sent_at=datetime.utcnow(),
                    status="sent"
                )
                
                db.add(communication)
                db.commit()
                db.refresh(communication)
                
                # Send email
                send_violation_notification_email(
                    resident.email, violation, notification_type, customized_message, current_user
                )
                
                # Create notification record
                notification = Notification(
                    communication_id=communication.id,
                    recipient_email=resident.email,
                    notification_type=notification_type,
                    status="sent",
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
                
                results.append({
                    "violation_id": violation_id,
                    "status": "success",
                    "recipient": resident.email
                })
                
            except Exception as e:
                results.append({
                    "violation_id": violation_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"Bulk notification completed for {len(violation_ids)} violations")
        
        return {
            "total_violations": len(violation_ids),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to send bulk notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send bulk notifications"
        )

@router.get("/communications/{violation_id}", response_model=List[CommunicationOut])
def get_violation_communications(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get all communications for a specific violation."""
    try:
        communications = db.query(Communication).filter(
            Communication.violation_id == violation_id
        ).order_by(Communication.sent_at.desc()).all()
        
        return communications
        
    except Exception as e:
        logger.error(f"Failed to get violation communications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communications"
        )

@router.get("/notifications", response_model=List[NotificationOut])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get notifications with optional filtering."""
    try:
        query = db.query(Notification)
        
        if status_filter:
            query = query.filter(Notification.status == status_filter)
        
        notifications = query.order_by(Notification.sent_at.desc()).offset(skip).limit(limit).all()
        
        return notifications
        
    except Exception as e:
        logger.error(f"Failed to get notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )

@router.post("/schedule-reminder")
def schedule_reminder(
    violation_id: int = Form(...),
    reminder_date: str = Form(...),  # ISO format
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Schedule a reminder for a violation."""
    try:
        # Parse reminder date
        reminder_dt = datetime.fromisoformat(reminder_date.replace('Z', '+00:00'))
        
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Create scheduled communication
        communication = Communication(
            violation_id=violation_id,
            sender_id=current_user.id,
            notification_type="reminder",
            message=message,
            scheduled_for=reminder_dt,
            status="scheduled"
        )
        
        db.add(communication)
        db.commit()
        db.refresh(communication)
        
        logger.info(f"Reminder scheduled for violation {violation_id} on {reminder_dt}")
        
        return {
            "communication_id": communication.id,
            "scheduled_for": reminder_dt,
            "status": "scheduled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule reminder"
        )

@router.post("/send-escalation")
def send_escalation(
    violation_id: int = Form(...),
    escalation_reason: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Send escalation notification to HOA board."""
    try:
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Violation not found"
            )
        
        # Get HOA board members
        hoa_board_members = db.query(User).filter(
            User.role == "hoa_board",
            User.hoa_id == violation.hoa_id
        ).all()
        
        if not hoa_board_members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No HOA board members found"
            )
        
        # Create escalation message
        escalation_message = f"""
        URGENT: Violation Escalation Required
        
        Violation #{violation.violation_number}
        Address: {violation.address}
        Resident: {violation.offender}
        Repeat Offender Score: {violation.repeat_offender_score}
        
        Escalation Reason: {escalation_reason}
        
        This violation requires immediate attention from the HOA board.
        """
        
        # Send to all HOA board members
        recipients = [member.email for member in hoa_board_members if member.email]
        
        # Create communication record
        communication = Communication(
            violation_id=violation_id,
            sender_id=current_user.id,
            notification_type="escalation",
            message=escalation_message,
            recipients=",".join(recipients),
            sent_at=datetime.utcnow(),
            status="sent"
        )
        
        db.add(communication)
        db.commit()
        db.refresh(communication)
        
        # Send emails
        for recipient_email in recipients:
            send_violation_notification_email(
                recipient_email, violation, "escalation", escalation_message, current_user
            )
            
            # Create notification record
            notification = Notification(
                communication_id=communication.id,
                recipient_email=recipient_email,
                notification_type="escalation",
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(notification)
        
        db.commit()
        
        # Update violation status
        db.query(Violation).filter(Violation.id == violation_id).update(
            {"status": "under_review"}
        )
        db.commit()
        
        logger.info(f"Escalation sent for violation {violation_id} to {len(recipients)} HOA board members")
        
        return {
            "communication_id": communication.id,
            "recipients_count": len(recipients),
            "status": "escalated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send escalation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send escalation"
        )

@router.get("/communication-stats")
def get_communication_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get communication statistics."""
    try:
        # Build query filters
        query_filters = []
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_filters.append(Communication.sent_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_filters.append(Communication.sent_at <= end_dt)
        
        # Get total communications
        total_communications = db.query(func.count(Communication.id)).filter(*query_filters).scalar()
        
        # Get communications by type
        type_counts = db.query(
            Communication.notification_type,
            func.count(Communication.id)
        ).filter(*query_filters).group_by(Communication.notification_type).all()
        
        # Get delivery success rate
        successful_notifications = db.query(func.count(Notification.id)).filter(
            *query_filters,
            Notification.status == "sent"
        ).scalar()
        
        total_notifications = db.query(func.count(Notification.id)).filter(*query_filters).scalar()
        success_rate = (successful_notifications / total_notifications * 100) if total_notifications > 0 else 0
        
        # Get average response time (if tracking responses)
        response_times = db.query(
            func.avg(
                func.extract('epoch', Notification.read_at - Notification.sent_at) / 3600
            )
        ).filter(
            *query_filters,
            Notification.read_at.isnot(None)
        ).scalar()
        
        avg_response_hours = float(response_times) if response_times else 0
        
        return {
            "total_communications": total_communications,
            "communications_by_type": {comm_type: count for comm_type, count in type_counts},
            "delivery_success_rate": round(success_rate, 2),
            "average_response_hours": round(avg_response_hours, 1),
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications
        }
        
    except Exception as e:
        logger.error(f"Failed to get communication stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication statistics"
        )

def get_resident_for_violation(violation: Violation, db: Session) -> Optional[Resident]:
    """Get resident for a violation."""
    try:
        # Try to find by address first
        resident = db.query(Resident).filter(
            Resident.address.ilike(f"%{violation.address}%")
        ).first()
        
        if not resident:
            # Try to find by offender name
            resident = db.query(Resident).filter(
                Resident.name.ilike(f"%{violation.offender}%")
            ).first()
        
        return resident
    except Exception as e:
        logger.warning(f"Failed to find resident for violation: {e}")
        return None

def customize_message(template: str, violation: Violation, resident: Resident) -> str:
    """Customize message template with violation and resident data."""
    try:
        customized = template.replace("{resident_name}", resident.name or "Resident")
        customized = customized.replace("{address}", violation.address or "Unknown Address")
        customized = customized.replace("{violation_number}", str(violation.violation_number or "N/A"))
        customized = customized.replace("{description}", violation.description or "N/A")
        customized = customized.replace("{date}", violation.timestamp.strftime("%B %d, %Y") if violation.timestamp else "N/A")
        
        return customized
    except Exception as e:
        logger.warning(f"Failed to customize message: {e}")
        return template

def send_violation_notification_email(
    recipient_email: str, 
    violation: Violation, 
    notification_type: str, 
    message: str, 
    sender: User
) -> None:
    """Send violation notification email."""
    try:
        subject = f"{notification_type.title()} - Violation #{violation.violation_number}"
        
        # TODO: Implement actual email sending
        logger.info(f"Violation notification email prepared for {recipient_email}")
        
    except Exception as e:
        logger.warning(f"Failed to send violation notification email: {e}")

def send_escalation_email(
    recipient_email: str, 
    violation: Violation, 
    escalation_reason: str, 
    sender: User
) -> None:
    """Send escalation email to HOA board member."""
    try:
        subject = f"URGENT: Violation Escalation - #{violation.violation_number}"
        
        # TODO: Implement actual email sending
        logger.info(f"Escalation email prepared for {recipient_email}")
        
    except Exception as e:
        logger.warning(f"Failed to send escalation email: {e}") 