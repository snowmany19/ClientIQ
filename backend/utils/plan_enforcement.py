# backend/utils/plan_enforcement.py

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, ContractRecord
from utils.auth_utils import get_current_user
from utils.stripe_utils import get_plan_limits

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
    
    # Get current user count for this workspace
    user_count = db.query(User).filter(
        User.workspace_id == current_user.workspace_id
    ).count()
    
    # Get plan limits
    plan_limits = get_plan_limits(current_user.plan_id)
    user_limit = plan_limits.get("users", 1)
    
    if user_count >= user_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "User limit exceeded for your current plan",
                "current_usage": user_count,
                "limit": user_limit,
                "upgrade_suggestion": "Consider upgrading to a plan with more users"
            }
        )
    
    return True

async def check_contract_limit(
    current_user: User,
    db: Session
) -> bool:
    """Check if user can create more contracts based on their plan."""
    if not current_user.plan_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription plan"
        )
    
    # Get current month's contract count
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    contract_count = db.query(ContractRecord).filter(
        ContractRecord.owner_user_id == current_user.id,
        ContractRecord.created_at >= start_of_month
    ).count()
    
    # Get plan limits
    plan_limits = get_plan_limits(current_user.plan_id)
    contract_limit = plan_limits.get("contracts_per_month", 10)
    
    if contract_count >= contract_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Contract limit exceeded for your current plan",
                "current_usage": contract_count,
                "limit": contract_limit,
                "upgrade_suggestion": "Consider upgrading to a plan with more contracts per month"
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
        "solo": ["ai_contract_analysis", "risk_assessment", "professional_reports", "contract_tracking", "email_support", "standard_templates"],
        "team": ["ai_contract_analysis", "risk_assessment", "professional_reports", "contract_tracking", "advanced_analytics", "ai_rewrite_suggestions", "priority_support", "team_collaboration"],
        "business": ["ai_contract_analysis", "risk_assessment", "professional_reports", "contract_tracking", "advanced_analytics", "ai_rewrite_suggestions", "priority_support", "custom_integrations", "legal_team_collaboration"],
        "enterprise": ["ai_contract_analysis", "risk_assessment", "professional_reports", "contract_tracking", "advanced_analytics", "ai_rewrite_suggestions", "priority_support", "custom_integrations", "multi_workspace_management", "dedicated_support", "compliance_tools"]
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
    
    # Get current month's contract count
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    contract_count = db.query(ContractRecord).filter(
        ContractRecord.owner_user_id == current_user.id,
        ContractRecord.created_at >= start_of_month
    ).count()
    
    # Get user count for this workspace
    user_count = db.query(User).filter(
        User.workspace_id == current_user.workspace_id
    ).count()
    
    limits = get_usage_limits(current_user.plan_id)
    
    return {
        "plan": current_user.plan_id,
        "usage": {
            "contracts_per_month": contract_count,
            "users": user_count
        },
        "limits": limits,
        "contracts_remaining": limits.get("contracts_per_month", -1) - contract_count if limits.get("contracts_per_month", -1) != -1 else -1,
        "users_remaining": limits.get("users", -1) - user_count if limits.get("users", -1) != -1 else -1
    } 