from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime, timezone, timedelta
import qrcode
import base64
import io
import secrets

from database import get_db
from models import User, UserSession, Violation
from routes.auth import get_current_user

router = APIRouter(prefix="/user-settings", tags=["user-settings"])

@router.get("/user-settings")
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current settings"""
    return {
        "notifications": {
            "email": current_user.notification_email,
            "push": current_user.notification_push,
            "violations": current_user.notification_violations,
            "reports": current_user.notification_reports,
        },
        "appearance": {
            "theme": current_user.theme_preference,
            "pwa_offline": current_user.pwa_offline_enabled,
            "pwa_app_switcher": current_user.pwa_app_switcher_enabled,
        },
        "security": {
            "two_factor_enabled": current_user.two_factor_enabled,
        }
    }

@router.put("/notifications")
def update_notification_preferences(
    preferences: Dict[str, bool],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences"""
    # Update user notification settings
    current_user.notification_email = preferences.get("email", True)
    current_user.notification_push = preferences.get("push", True)
    current_user.notification_violations = preferences.get("violations", True)
    current_user.notification_reports = preferences.get("reports", True)
    
    db.commit()
    return {"message": "Notification preferences updated successfully"}

@router.put("/appearance")
def update_appearance_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user appearance settings"""
    # Update user appearance settings
    current_user.theme_preference = settings.get("theme", "light")
    current_user.pwa_offline_enabled = settings.get("pwa_offline", True)
    current_user.pwa_app_switcher_enabled = settings.get("pwa_app_switcher", True)
    
    db.commit()
    return {"message": "Appearance settings updated successfully"}

@router.get("/export-data")
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user data as JSON"""
    from fastapi.responses import Response
    
    # Get user's violations
    violations = db.query(Violation).filter(Violation.user_id == current_user.id).all()
    
    # Create comprehensive user data export
    user_data = {
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "subscription_status": current_user.subscription_status,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
            "settings": {
                "theme_preference": current_user.theme_preference,
                "notification_email": current_user.notification_email,
                "notification_push": current_user.notification_push,
                "notification_violations": current_user.notification_violations,
                "notification_reports": current_user.notification_reports,
                "pwa_offline_enabled": current_user.pwa_offline_enabled,
                "pwa_app_switcher_enabled": current_user.pwa_app_switcher_enabled,
            }
        },
        "violations": [
            {
                "id": v.id,
                "violation_number": v.violation_number,
                "description": v.description,
                "status": v.status,
                "timestamp": v.timestamp.isoformat() if v.timestamp else None,
                "address": v.address,
                "offender": v.offender,
            }
            for v in violations
        ],
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0"
    }
    
    # Convert to JSON
    json_data = json.dumps(user_data, indent=2, default=str)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"
        }
    )

@router.get("/active-sessions")
def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active sessions"""
    # Get real active sessions from database
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).all()
    
    return [
        {
            "id": str(session.id),
            "device": session.device_info or "Unknown Device",
            "location": session.location or "Unknown Location",
            "last_activity": f"{int((datetime.utcnow() - session.last_activity_at).total_seconds() / 60)} minutes ago" if session.last_activity_at else "Unknown",
            "ip_address": session.ip_address or "Unknown",
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat()
        }
        for session in active_sessions
    ]

@router.delete("/revoke-session/{session_id}")
def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    # Find and deactivate the session
    session = db.query(UserSession).filter(
        UserSession.id == int(session_id),
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    db.commit()
    
    return {"message": f"Session {session_id} revoked successfully"}

@router.get("/2fa-status")
def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's 2FA status"""
    return {"enabled": current_user.two_factor_enabled}

@router.post("/enable-2fa")
def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable two-factor authentication"""
    # Generate a secret key
    secret = secrets.token_hex(16)
    
    # Store the secret in the user record
    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = True
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"otpauth://totp/CivicLogHOA:{current_user.username}?secret={secret}&issuer=CivicLogHOA")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    db.commit()
    
    return {
        "qr_code": f"data:image/png;base64,{qr_code_base64}",
        "secret": secret,
        "message": "2FA enabled successfully"
    }

@router.delete("/disable-2fa")
def disable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable two-factor authentication"""
    # Remove the 2FA secret and disable 2FA
    current_user.two_factor_secret = None
    current_user.two_factor_enabled = False
    db.commit()
    
    return {"message": "2FA disabled successfully"} 