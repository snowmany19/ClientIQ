from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime, timezone, timedelta
import qrcode
import base64
import io
import secrets
import pyotp

from database import get_db
from models import User, UserSession
from utils.auth_utils import get_current_user

router = APIRouter(tags=["user-settings"])

@router.get("/user-settings")
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current settings"""
    try:
        return {
            "notifications": {
                "email": current_user.notification_email if current_user.notification_email is not None else True,
                "push": current_user.notification_push if current_user.notification_push is not None else True,
                "contracts": current_user.notification_contracts if current_user.notification_contracts is not None else True,
                "reports": current_user.notification_reports if current_user.notification_reports is not None else True,
            },
            "appearance": {
                "theme": current_user.theme_preference if current_user.theme_preference else "light",
                "pwa_offline": current_user.pwa_offline_enabled if current_user.pwa_offline_enabled is not None else True,
                "pwa_app_switcher": current_user.pwa_app_switcher_enabled if current_user.pwa_app_switcher_enabled is not None else True,
            },
            "security": {
                "two_factor_enabled": current_user.two_factor_enabled if current_user.two_factor_enabled is not None else False,
            }
        }
    except Exception as e:
        # Return default settings if there's an error
        return {
            "notifications": {
                "email": True,
                "push": True,
                "contracts": True,
                "reports": True,
            },
            "appearance": {
                "theme": "light",
                "pwa_offline": True,
                "pwa_app_switcher": True,
            },
            "security": {
                "two_factor_enabled": False,
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
    current_user.notification_contracts = preferences.get("contracts", True)
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
    
    # Get user's contracts instead of violations
    from models import ContractRecord
    contracts = db.query(ContractRecord).filter(ContractRecord.owner_user_id == current_user.id).all()
    
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
                "notification_contracts": current_user.notification_contracts,
                "notification_reports": current_user.notification_reports,
                "pwa_offline_enabled": current_user.pwa_offline_enabled,
                "pwa_app_switcher_enabled": current_user.pwa_app_switcher_enabled,
            }
        },
        "contracts": [
            {
                "id": c.id,
                "title": c.title,
                "counterparty": c.counterparty,
                "category": c.category,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "effective_date": c.effective_date.isoformat() if c.effective_date else None,
            }
            for c in contracts
        ]
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
    qr.add_data(f"otpauth://totp/ContractGuard:{current_user.username}?secret={secret}&issuer=ContractGuard")
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

@router.post("/verify-2fa")
def verify_2fa(
    verification_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify 2FA setup with a code"""
    code = verification_data.get("code")
    
    if not code or len(code) != 6:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    
    # Verify the TOTP code
    totp = pyotp.TOTP(current_user.two_factor_secret)
    
    if totp.verify(code):
        # 2FA is now fully enabled
        current_user.two_factor_enabled = True
        db.commit()
        return {"message": "2FA verification successful", "enabled": True}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")

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