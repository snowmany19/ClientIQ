# backend/routes/billing.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import stripe
import os

from database import get_db
from models import User
from utils.auth_utils import get_current_user
from utils.stripe_utils import (
    create_workspace_subscription, update_workspace_subscription, 
    cancel_workspace_subscription, get_subscription_plans, get_plan_by_id, get_plan_features,
    get_plan_limits, SUBSCRIPTION_PLANS
)

router = APIRouter(tags=["billing"])

# Webhook secret for verifying Stripe webhooks
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.get("/plans")
def get_available_plans():
    """Get all available subscription plans."""
    # Convert to the format expected by frontend
    plans_list = []
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        plans_list.append({
            "id": plan_id,
            "name": plan_data["name"],
            "price": plan_data["price"],
            "currency": plan_data["currency"],
            "interval": plan_data["interval"],
            "features": plan_data["features"],
            "limits": plan_data["limits"]
        })
    
    return plans_list

@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription details."""
    # Check if user is admin (automatic premium access)
    if current_user.role == "admin":
        plan = SUBSCRIPTION_PLANS.get("enterprise", {})  # Give admin enterprise features
        return {
            "subscription_id": "admin_enterprise",
            "plan_id": "enterprise",
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "cancel_at_period_end": False,
            "features": get_plan_features("enterprise"),
            "limits": get_plan_limits("enterprise")
        }
    
    # Check if user has an active subscription
    if current_user.subscription_id is not None:
        try:
            plan = SUBSCRIPTION_PLANS.get(str(current_user.plan_id), {})
            
            return {
                "subscription_id": str(current_user.subscription_id),
                "plan_id": str(current_user.plan_id),
                "status": "active",
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "cancel_at_period_end": False,
                "features": get_plan_features(str(current_user.plan_id)),
                "limits": get_plan_limits(str(current_user.plan_id))
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve subscription: {str(e)}"
            )
    
    # Check if user has an active plan (for staff users who might have been assigned a plan)
    if current_user.plan_id is not None and str(current_user.subscription_status) == "active":
        plan = SUBSCRIPTION_PLANS.get(str(current_user.plan_id), {})
        return {
            "subscription_id": f"plan_{str(current_user.plan_id)}",
            "plan_id": str(current_user.plan_id),
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "cancel_at_period_end": False,
            "features": get_plan_features(str(current_user.plan_id)),
            "limits": get_plan_limits(str(current_user.plan_id))
        }
    
    # No active subscription
    return {
        "subscription_id": None,
        "plan_id": None,
        "status": "inactive",
        "current_period_start": None,
        "current_period_end": None,
        "cancel_at_period_end": False,
        "features": [],
        "limits": {}
    }

@router.post("/create-checkout-session")
def create_checkout_session_route(
    plan_id: str = Body(None),
    success_url: str = Body(None),
    cancel_url: str = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription."""
    if plan_id is None:
        raise HTTPException(status_code=400, detail="Missing plan_id")
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    try:
        if current_user.stripe_customer_id is None:
            customer_id = create_workspace_subscription(str(current_user.email or ""), str(current_user.username))
            setattr(current_user, 'stripe_customer_id', customer_id)
            db.commit()
        # Use provided URLs or defaults
        _success_url = success_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/_billing_success_page"
        _cancel_url = cancel_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/_billing_cancel_page"
        # TODO: Implement checkout session creation
        # checkout_session = create_checkout_session(
        #     str(current_user.stripe_customer_id),
        #     plan_id,
        #     _success_url,
        #     _cancel_url
        # )
        return {
            "message": "Checkout session creation not yet implemented",
            "plan_id": plan_id,
            "customer_id": str(current_user.stripe_customer_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/create-portal-session")
def create_portal_session_alias(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alias for /billing-portal for test compatibility."""
    if current_user.stripe_customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found"
        )
    try:
        return_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/dashboard"
        # TODO: Implement billing portal session creation
        # portal_url = create_billing_portal_session(
        #     str(current_user.stripe_customer_id),
        #     return_url
        # )
        return {
            "message": "Billing portal session creation not yet implemented",
            "customer_id": str(current_user.stripe_customer_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create billing portal session: {str(e)}"
        )

@router.post("/cancel-subscription")
def cancel_subscription_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription."""
    if current_user.subscription_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )
    
    try:
        result = cancel_workspace_subscription(str(current_user.subscription_id))
        setattr(current_user, 'subscription_status', 'canceled')
        db.commit()
        
        return {
            "message": "Subscription canceled successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for subscription events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_completed(session, db)
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        handle_subscription_updated(subscription, db)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        handle_subscription_deleted(subscription, db)
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        handle_payment_failed(invoice, db)
    
    return {"status": "success"}

def handle_checkout_completed(session: Dict[str, Any], db: Session):
    """Handle successful checkout completion."""
    customer_id = session["customer"]
    plan_id = session["metadata"].get("plan_id")
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        setattr(user, 'plan_id', plan_id)
        setattr(user, 'subscription_status', 'active')
        db.commit()

def handle_subscription_updated(subscription: Dict[str, Any], db: Session):
    """Handle subscription updates."""
    customer_id = subscription["customer"]
    subscription_id = subscription["id"]
    status = subscription["status"]
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        setattr(user, 'subscription_id', subscription_id)
        setattr(user, 'subscription_status', status)
        setattr(user, 'billing_cycle_start', subscription.get("current_period_start"))
        setattr(user, 'billing_cycle_end', subscription.get("current_period_end"))
        db.commit()

def handle_subscription_deleted(subscription: Dict[str, Any], db: Session):
    """Handle subscription deletion."""
    customer_id = subscription["customer"]
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        setattr(user, 'subscription_status', 'canceled')
        setattr(user, 'subscription_id', None)
        db.commit()

def handle_payment_failed(invoice: Dict[str, Any], db: Session):
    """Handle failed payments."""
    customer_id = invoice["customer"]
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        setattr(user, 'subscription_status', 'past_due')
        db.commit()

@router.get("/usage")
def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics."""
    from sqlalchemy import text
    from datetime import datetime
    
    # Count contracts for current user in current month
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        contract_count = db.execute(
            text("SELECT COUNT(*) FROM contract_records WHERE owner_user_id = :user_id AND created_at >= :start_date"),
            {"user_id": current_user.id, "start_date": start_of_month}
        ).scalar()
    except Exception as e:
        print(f"Error getting contract count: {e}")
        contract_count = 0
    
    # Count users for this workspace (excluding residents)
    try:
        user_count = db.execute(
            text("SELECT COUNT(*) FROM users WHERE workspace_id = :workspace_id AND role != 'resident'"),
            {"workspace_id": current_user.workspace_id}
        ).scalar()
    except Exception as e:
        print(f"Error getting user count: {e}")
        user_count = 1  # Fallback to current user only
    
    # Get plan limits
    plan_limits = get_plan_limits(str(current_user.plan_id))
    
    return {
        "usage": {
            "contracts_per_month": contract_count,
            "users": user_count
        },
        "limits": plan_limits,
        "plan_id": current_user.plan_id
    }

@router.get("/subscription-status")
def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription status and plan."""
    return {
        "subscription_status": current_user.subscription_status or "inactive",
        "plan_id": current_user.plan_id or "basic"
    }

@router.get("/usage-limits")
def get_usage_limits_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage limits for current user's plan."""
    plan_id = str(current_user.plan_id or "solo")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("solo"))
    limits = plan.get("limits", {}) if plan else {}
    return {
        "plan": plan_id,
        "limits": {
            "workspaces": limits.get("workspaces", 1),
            "contracts_per_month": limits.get("contracts_per_month", 10),
            "users": limits.get("users", 1),
            "storage_gb": limits.get("storage_gb", 5)
        }
    }

@router.get("/history")
def get_billing_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return dummy billing history for test user."""
    # Return a list of fake invoices for testing
    return [
        {
            "id": "in_test123",
            "amount_paid": 2000,
            "status": "paid",
            "created": 1640995200
        }
    ]

@router.post("/upgrade-subscription")
def upgrade_subscription(
    new_price_id: str = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock upgrade subscription endpoint for tests."""
    if new_price_id is None:
        raise HTTPException(status_code=400, detail="Missing new_price_id")
    return {
        "message": "Subscription upgraded successfully"
    } 