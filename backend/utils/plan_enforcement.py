# backend/utils/plan_enforcement.py

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, Violation
from utils.auth_utils import get_current_user
from utils.stripe_utils import enforce_plan_limits, get_plan_upgrade_suggestion, get_usage_limits

def check_violation_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """Check if user can create more violations based on their plan."""
    if not current_user.plan_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription plan"
        )
    
    # Get current month's violation count
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    violation_count = db.query(Violation).filter(
        Violation.user_id == current_user.id,
        Violation.timestamp >= start_of_month
    ).count()
    
    current_usage = {"violations_per_month": violation_count}
    
    if not enforce_plan_limits(current_user.plan_id, current_usage, "violations_per_month"):
        upgrade_suggestion = get_plan_upgrade_suggestion(
            current_user.plan_id, 
            current_usage, 
            "violations_per_month"
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Violation limit exceeded for your current plan",
                "current_usage": violation_count,
                "upgrade_suggestion": upgrade_suggestion
            }
        )
    
    return True

def check_user_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """Check if user can create more users based on their plan."""
    if not current_user.plan_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription plan"
        )
    
    # Get current user count for this HOA
    user_count = db.query(User).filter(
        User.hoa_id == current_user.hoa_id
    ).count()
    
    current_usage = {"users": user_count}
    
    if not enforce_plan_limits(current_user.plan_id, current_usage, "users"):
        upgrade_suggestion = get_plan_upgrade_suggestion(
            current_user.plan_id, 
            current_usage, 
            "users"
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "User limit exceeded for your current plan",
                "current_usage": user_count,
                "upgrade_suggestion": upgrade_suggestion
            }
        )
    
    return True

def require_active_subscription(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require an active subscription to access premium features."""
    if not current_user.plan_id or current_user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required for this feature"
        )
    return current_user

def require_plan_feature(
    feature: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """Require a specific plan feature to access functionality."""
    if not current_user.plan_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription required for this feature"
        )
    
    # Define feature requirements for each plan
    plan_features = {
        "starter": ["basic_violations", "standard_letters", "email_support"],
        "professional": ["basic_violations", "standard_letters", "email_support", 
                        "advanced_analytics", "ai_letters", "priority_support"],
        "enterprise": ["basic_violations", "standard_letters", "email_support", 
                      "advanced_analytics", "ai_letters", "priority_support",
                      "dedicated_support", "custom_integrations", "compliance_tools"]
    }
    
    user_features = plan_features.get(current_user.plan_id, [])
    
    if feature not in user_features:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature '{feature}' requires a higher plan tier"
        )
    
    return current_user

def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current usage statistics for the user's plan."""
    if not current_user.plan_id:
        return {"error": "No active subscription"}
    
    # Get current month's violation count
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    violation_count = db.query(Violation).filter(
        Violation.user_id == current_user.id,
        Violation.timestamp >= start_of_month
    ).count()
    
    # Get user count for this HOA
    user_count = db.query(User).filter(
        User.hoa_id == current_user.hoa_id
    ).count()
    
    limits = get_usage_limits(current_user.plan_id)
    
    return {
        "plan": current_user.plan_id,
        "usage": {
            "violations_per_month": violation_count,
            "users": user_count
        },
        "limits": limits,
        "violations_remaining": limits.get("violations_per_month", -1) - violation_count if limits.get("violations_per_month", -1) != -1 else -1,
        "users_remaining": limits.get("users", -1) - user_count if limits.get("users", -1) != -1 else -1
    } 