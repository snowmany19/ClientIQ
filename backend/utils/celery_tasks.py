# backend/utils/celery_tasks.py
# Celery tasks for ContractGuard.ai - AI Contract Review Platform

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from celery import Celery
from sqlalchemy.orm import Session

from utils.cache import invalidate_user_cache, invalidate_workspace_cache
from utils.logger import get_logger

logger = get_logger("celery_tasks")

# Celery app configuration
celery_app = Celery(
    "contractguard",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# ===========================
# 📄 Contract Analysis Tasks
# ===========================

@celery_app.task(bind=True, max_retries=3)
def analyze_contract_async(self, contract_id: int, user_id: int):
    """Analyze contract asynchronously using AI."""
    try:
        from database import SessionLocal
        from models import ContractRecord, User
        from utils.contract_analyzer import analyze_contract
        
        db = SessionLocal()
        
        # Get contract and user
        contract = db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not contract or not user:
            return {"status": "error", "message": "Contract or user not found"}
        
        # Perform AI analysis
        analysis_result = analyze_contract(contract, user)
        
        # Update contract with analysis results
        contract.analysis_json = analysis_result
        contract.status = "analyzed"
        contract.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Invalidate caches
        if contract.workspace_id:
            invalidate_workspace_cache(contract.workspace_id)
        
        logger.info(f"Contract analysis completed for contract {contract_id}")
        return {"status": "success", "analysis": analysis_result}
        
    except Exception as e:
        logger.error(f"Contract analysis failed for contract {contract_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task(bind=True, max_retries=3)
def generate_contract_summary_async(self, contract_id: int):
    """Generate contract summary asynchronously."""
    try:
        from database import SessionLocal
        from models import ContractRecord
        from utils.summary_generator import generate_contract_summary
        
        db = SessionLocal()
        
        # Get contract
        contract = db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()
        
        if not contract:
            return {"status": "error", "message": "Contract not found"}
        
        # Generate summary
        summary = generate_contract_summary(contract)
        
        # Update contract
        contract.summary_text = summary
        contract.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Contract summary generated for contract {contract_id}")
        return {"status": "success", "summary": summary}
        
    except Exception as e:
        logger.error(f"Contract summary generation failed for contract {contract_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

# ===========================
# 📧 Email and Notification Tasks
# ===========================

@celery_app.task(bind=True, max_retries=3)
def send_email_async(self, to_email: str, subject: str, body: str, email_type: str = "general"):
    """Send email asynchronously."""
    try:
        from utils.email_service import send_email
        
        result = send_email(to_email, subject, body, email_type)
        
        if result["status"] == "success":
            logger.info(f"Email sent successfully to {to_email}")
            return {"status": "success", "message": "Email sent successfully"}
        else:
            raise Exception(result.get("message", "Email sending failed"))
            
    except Exception as e:
        logger.error(f"Email sending failed to {to_email}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, max_retries=3)
def send_notification_async(self, user_id: int, title: str, message: str, notification_type: str = "general"):
    """Send notification asynchronously."""
    try:
        from database import SessionLocal
        from models import Notification
        
        db = SessionLocal()
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        db.add(notification)
        db.commit()
        
        logger.info(f"Notification sent to user {user_id}")
        return {"status": "success", "notification_id": notification.id}
        
    except Exception as e:
        logger.error(f"Notification sending failed for user {user_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

# ===========================
# 📊 Analytics and Reporting Tasks
# ===========================

@celery_app.task(bind=True, max_retries=3)
def generate_analytics_report_async(self, workspace_id: int, report_type: str = "monthly"):
    """Generate analytics report asynchronously."""
    try:
        from database import SessionLocal
        from models import ContractRecord, Workspace
        from utils.cache import cache_analytics_data
        import pandas as pd
        
        db = SessionLocal()
        
        # Get contracts for workspace
        contracts = db.query(ContractRecord).filter(ContractRecord.workspace_id == workspace_id).all()
        
        if not contracts:
            return {"status": "error", "message": "No contracts found for workspace"}
        
        # Generate analytics data
        df = pd.DataFrame([{
            'id': c.id,
            'created_at': c.created_at,
            'status': c.status,
            'category': c.category,
        } for c in contracts])
        
        # Calculate analytics
        analytics_data = {
            "total_contracts": len(contracts),
            "pending_contracts": len(df[df['status'] == 'pending']),
            "analyzed_contracts": len(df[df['status'] == 'analyzed']),
            "approved_contracts": len(df[df['status'] == 'approved']),
            "contracts_by_category": df['category'].value_counts().to_dict(),
            "contracts_by_month": df.groupby(df['created_at'].dt.to_period('M')).size().to_dict(),
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Cache the analytics data
        cache_analytics_data(workspace_id, analytics_data, expire_time=3600)
        
        logger.info(f"Analytics report generated for workspace {workspace_id}")
        return {"status": "success", "analytics": analytics_data}
        
    except Exception as e:
        logger.error(f"Analytics generation failed for workspace {workspace_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

# ===========================
# 🔄 Maintenance and Cleanup Tasks
# ===========================

@celery_app.task
def cleanup_expired_sessions():
    """Clean up expired user sessions."""
    try:
        from database import SessionLocal
        from models import UserSession
        
        db = SessionLocal()
        
        # Delete expired sessions
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.delete(session)
        
        db.commit()
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return {"status": "success", "cleaned_sessions": len(expired_sessions)}
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

@celery_app.task
def cleanup_expired_notifications():
    """Clean up expired notifications."""
    try:
        from database import SessionLocal
        from models import Notification
        
        db = SessionLocal()
        
        # Delete expired notifications
        expired_notifications = db.query(Notification).filter(
            Notification.expires_at < datetime.utcnow()
        ).all()
        
        for notification in expired_notifications:
            db.delete(notification)
        
        db.commit()
        
        logger.info(f"Cleaned up {len(expired_notifications)} expired notifications")
        return {"status": "success", "cleaned_notifications": len(expired_notifications)}
        
    except Exception as e:
        logger.error(f"Notification cleanup failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close()

# ===========================
# 📈 Performance Monitoring Tasks
# ===========================

@celery_app.task
def record_performance_metrics():
    """Record system performance metrics."""
    try:
        from database import SessionLocal
        from models import PerformanceMetrics
        import psutil
        import time
        
        db = SessionLocal()
        
        # Collect system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Record metrics
        metrics = [
            PerformanceMetrics(
                metric_name="cpu_usage",
                metric_value=cpu_percent,
                metric_unit="percent"
            ),
            PerformanceMetrics(
                metric_name="memory_usage",
                metric_value=memory.percent,
                metric_unit="percent"
            ),
            PerformanceMetrics(
                metric_name="disk_usage",
                metric_value=disk.percent,
                metric_unit="percent"
            )
        ]
        
        for metric in metrics:
            db.add(metric)
        
        db.commit()
        
        logger.info("Performance metrics recorded successfully")
        return {"status": "success", "metrics_recorded": len(metrics)}
        
    except Exception as e:
        logger.error(f"Performance metrics recording failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'db' in locals():
            db.close() 