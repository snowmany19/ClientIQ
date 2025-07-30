# Background task processing with Celery
# utils/celery_tasks.py

import os
from celery import Celery
from datetime import datetime
from typing import Optional
from utils.logger import get_logger
from utils.cache import invalidate_user_cache, invalidate_hoa_cache
from utils.email_alerts import send_violation_notification_email

# Configure Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

celery_app = Celery(
    'civicloghoa',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['utils.celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

logger = get_logger("celery")

@celery_app.task(bind=True, max_retries=3)
def generate_violation_pdf_async(self, violation_id: int):
    """Generate PDF for violation asynchronously."""
    try:
        from database import SessionLocal
        from models import Violation
        from utils.pdf import generate_violation_pdf
        
        db = SessionLocal()
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            logger.error(f"Violation {violation_id} not found for PDF generation")
            return {"status": "error", "message": "Violation not found"}
        
        # Generate PDF
        pdf_path = generate_violation_pdf(violation)
        
        # Update violation with PDF path
        violation.pdf_path = pdf_path
        db.commit()
        
        # Invalidate related caches
        invalidate_user_cache(violation.user_id)
        if violation.hoa_id:
            invalidate_hoa_cache(violation.hoa_id)
        
        logger.info(f"PDF generated successfully for violation {violation_id}: {pdf_path}")
        return {"status": "success", "pdf_path": pdf_path}
        
    except Exception as e:
        logger.error(f"PDF generation failed for violation {violation_id}: {e}")
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task(bind=True, max_retries=3)
def send_email_notification_async(self, user_id: int, violation_id: int, notification_type: str = "new_violation"):
    """Send email notification asynchronously."""
    try:
        from database import SessionLocal
        from models import User, Violation
        from utils.email_alerts import send_email_alert
        
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not user or not violation:
            logger.error(f"User {user_id} or violation {violation_id} not found for email notification")
            return {"status": "error", "message": "User or violation not found"}
        
        # Send email notification
        success = send_violation_notification_email(
            user_email=user.email,
            user_name=user.username,
            violation_data={
                "violation_number": violation.violation_number,
                "description": violation.description,
                "address": violation.address,
                "location": violation.location,
                "timestamp": violation.timestamp.isoformat() if violation.timestamp else "",
                "status": violation.status
            }
        )
        
        if success:
            logger.info(f"Email notification sent successfully for violation {violation_id}")
            return {"status": "success", "email_sent": True}
        else:
            logger.error(f"Failed to send email notification for violation {violation_id}")
            return {"status": "error", "message": "Email sending failed"}
        
    except Exception as e:
        logger.error(f"Email notification failed for violation {violation_id}: {e}")
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task(bind=True, max_retries=3)
def send_reminder_notification(self, violation_id: int, reminder_date_str: str):
    """Send reminder notification for a violation."""
    try:
        from database import SessionLocal
        from models import Violation, Resident
        from utils.email_service import email_service
        
        db = SessionLocal()
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        
        if not violation:
            logger.error(f"Violation {violation_id} not found for reminder notification")
            return {"status": "error", "message": "Violation not found"}
        
        # Find resident by address or offender name
        address_str = getattr(violation, 'address', '') or ''
        offender_str = getattr(violation, 'offender', '') or ''
        
        resident = None
        if address_str:
            resident = db.query(Resident).filter(
                Resident.address.ilike(f"%{address_str}%")
            ).first()
        
        if not resident and offender_str:
            resident = db.query(Resident).filter(
                Resident.name.ilike(f"%{offender_str}%")
            ).first()
        
        # Send reminder email
        if resident and resident.email:
            success = email_service.send_follow_up_notice(
                violation=violation,
                recipient_email=resident.email,
                follow_up_data={
                    'violation_number': getattr(violation, 'violation_number', ''),
                    'description': getattr(violation, 'description', ''),
                    'address': address_str,
                    'location': getattr(violation, 'location', ''),
                    'timestamp': getattr(violation, 'timestamp', datetime.utcnow()).isoformat(),
                    'repeat_offender_score': getattr(violation, 'repeat_offender_score', 1),
                    'resident_name': getattr(resident, 'name', offender_str),
                    'resident_email': resident.email,
                    'resident_phone': getattr(resident, 'phone', ''),
                    'hoa_name': getattr(violation, 'hoa_name', ''),
                }
            )
            
            if success:
                logger.info(f"Reminder notification sent for violation {violation_id} to {resident.email}")
                return {"status": "success", "reminder_sent": True}
            else:
                logger.warning(f"Failed to send reminder notification for violation {violation_id}")
                return {"status": "error", "message": "Email sending failed"}
        else:
            logger.warning(f"No resident email found for violation {violation_id} reminder")
            return {"status": "error", "message": "No resident email found"}
        
    except Exception as e:
        logger.error(f"Reminder notification failed for violation {violation_id}: {e}")
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task(bind=True, max_retries=3)
def process_image_upload_async(self, image_path: str, violation_id: int):
    """Process uploaded image asynchronously (resize, optimize, etc.)."""
    try:
        from PIL import Image
        import os
        
        # Open and process image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')
            
            # Resize if too large (max 1200x800)
            if img.size[0] > 1200 or img.size[1] > 800:
                img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            
            # Save optimized version
            optimized_path = image_path.replace('.', '_optimized.')
            img.save(optimized_path, 'JPEG', quality=85, optimize=True)
            
            # Update violation with optimized image path
            from database import SessionLocal
            from models import Violation
            
            db = SessionLocal()
            violation = db.query(Violation).filter(Violation.id == violation_id).first()
            if violation:
                violation.image_url = optimized_path
                db.commit()
            
            db.close()
            
            logger.info(f"Image processed successfully for violation {violation_id}")
            return {"status": "success", "optimized_path": optimized_path}
        
    except Exception as e:
        logger.error(f"Image processing failed for violation {violation_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, max_retries=3)
def generate_analytics_report_async(self, hoa_id: int, report_type: str = "monthly"):
    """Generate analytics report asynchronously."""
    try:
        from database import SessionLocal
        from models import Violation, HOA
        from utils.cache import cache_analytics_data
        import pandas as pd
        
        db = SessionLocal()
        
        # Get violations for HOA
        violations = db.query(Violation).filter(Violation.hoa_id == hoa_id).all()
        
        if not violations:
            return {"status": "error", "message": "No violations found for HOA"}
        
        # Generate analytics data
        df = pd.DataFrame([{
            'id': v.id,
            'timestamp': v.timestamp,
            'status': v.status,
            'repeat_offender_score': v.repeat_offender_score,
        } for v in violations])
        
        # Calculate analytics
        analytics_data = {
            "total_violations": len(violations),
            "open_violations": len(df[df['status'] == 'open']),
            "resolved_violations": len(df[df['status'] == 'resolved']),
            "average_repeat_score": df['repeat_offender_score'].mean(),
            "violations_by_month": df.groupby(df['timestamp'].dt.to_period('M')).size().to_dict(),
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Cache the analytics data
        cache_analytics_data(hoa_id, analytics_data, expire_time=3600)
        
        logger.info(f"Analytics report generated for HOA {hoa_id}")
        return {"status": "success", "analytics": analytics_data}
        
    except Exception as e:
        logger.error(f"Analytics generation failed for HOA {hoa_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task(bind=True, max_retries=3)
def cleanup_expired_sessions_async(self):
    """Clean up expired user sessions asynchronously."""
    try:
        from database import SessionLocal
        from models import UserSession
        from datetime import datetime
        
        db = SessionLocal()
        
        # Delete expired sessions
        expired_count = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {expired_count} expired sessions")
        return {"status": "success", "expired_sessions_cleaned": expired_count}
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300)  # Retry in 5 minutes
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, max_retries=3)
def warm_cache_async(self):
    """Warm up cache asynchronously."""
    try:
        from utils.cache import warm_cache
        warm_cache()
        logger.info("Cache warming completed asynchronously")
        return {"status": "success", "cache_warmed": True}
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300)
        return {"status": "error", "message": str(e)}

# Periodic tasks (run on schedule)
@celery_app.task
def scheduled_cache_warming():
    """Scheduled task to warm cache every hour."""
    return warm_cache_async.delay()

@celery_app.task
def scheduled_session_cleanup():
    """Scheduled task to clean up expired sessions daily."""
    return cleanup_expired_sessions_async.delay()

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'warm-cache-hourly': {
        'task': 'utils.celery_tasks.scheduled_cache_warming',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-sessions-daily': {
        'task': 'utils.celery_tasks.scheduled_session_cleanup',
        'schedule': 86400.0,  # Every day
    },
} 