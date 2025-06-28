# backend/routes/billing.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import stripe
import os

from database import get_db
from models import User, Incident
from utils.auth_utils import get_current_user
from utils.stripe_utils import (
    create_customer, create_subscription, get_subscription,
    cancel_subscription, create_checkout_session, create_billing_portal_session,
    SUBSCRIPTION_PLANS, get_usage_limits, check_usage_limit, get_plan_features
)

router = APIRouter(prefix="/billing", tags=["billing"])

# Webhook secret for verifying Stripe webhooks
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.get("/plans")
def get_available_plans():
    """Get all available subscription plans."""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "message": "Available subscription plans"
    }

@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription details."""
    if not current_user.subscription_id:
        return {
            "subscription": None,
            "plan": None,
            "message": "No active subscription"
        }
    
    try:
        stripe_subscription = get_subscription(current_user.subscription_id)
        plan = SUBSCRIPTION_PLANS.get(current_user.plan_id, {})
        
        return {
            "subscription": stripe_subscription,
            "plan": plan,
            "features": get_plan_features(current_user.plan_id),
            "limits": get_usage_limits(current_user.plan_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve subscription: {str(e)}"
        )

@router.post("/create-checkout-session")
def create_checkout_session_route(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription."""
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    
    try:
        # Create Stripe customer if doesn't exist
        if not current_user.stripe_customer_id:
            customer_id = create_customer(current_user.email or "", current_user.username)
            current_user.stripe_customer_id = customer_id
            db.commit()
        
        # Create checkout session
        success_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/billing/success"
        cancel_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/billing/cancel"
        
        checkout_url = create_checkout_session(
            current_user.stripe_customer_id,
            plan_id,
            success_url,
            cancel_url
        )
        
        return {
            "checkout_url": checkout_url,
            "message": "Checkout session created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/billing-portal")
def create_billing_portal_session_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a billing portal session for customer management."""
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found"
        )
    
    try:
        return_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8501')}/dashboard"
        portal_url = create_billing_portal_session(
            current_user.stripe_customer_id,
            return_url
        )
        
        return {
            "portal_url": portal_url,
            "message": "Billing portal session created"
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
    if not current_user.subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )
    
    try:
        result = cancel_subscription(current_user.subscription_id)
        current_user.subscription_status = "canceled"
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
        user.plan_id = plan_id
        user.subscription_status = "active"
        db.commit()

def handle_subscription_updated(subscription: Dict[str, Any], db: Session):
    """Handle subscription updates."""
    customer_id = subscription["customer"]
    subscription_id = subscription["id"]
    status = subscription["status"]
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_id = subscription_id
        user.subscription_status = status
        user.billing_cycle_start = subscription.get("current_period_start")
        user.billing_cycle_end = subscription.get("current_period_end")
        db.commit()

def handle_subscription_deleted(subscription: Dict[str, Any], db: Session):
    """Handle subscription deletion."""
    customer_id = subscription["customer"]
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = "canceled"
        user.subscription_id = None
        db.commit()

def handle_payment_failed(invoice: Dict[str, Any], db: Session):
    """Handle failed payments."""
    customer_id = invoice["customer"]
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = "past_due"
        db.commit()

@router.get("/usage")
def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics."""
    # Count incidents for current user/store
    incident_count = db.query(Incident).filter(
        Incident.user_id == current_user.id
    ).count()
    
    # Get plan limits
    limits = get_usage_limits(current_user.plan_id)
    
    return {
        "usage": {
            "incidents": incident_count,
            "users": 1  # Current user
        },
        "limits": limits,
        "plan_id": current_user.plan_id
    } 