# backend/utils/stripe_utils.py

import os
import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic Plan",
        "price_id": os.getenv("STRIPE_BASIC_PRICE_ID"),
        "price": 29,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Up to 5 users",
            "Basic incident reporting",
            "AI-powered summaries",
            "PDF reports",
            "Email support"
        ],
        "limits": {
            "users": 5,
            "incidents_per_month": 100,
            "storage_gb": 1
        }
    },
    "pro": {
        "name": "Pro Plan",
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
        "price": 99,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Up to 25 users",
            "Advanced analytics",
            "Role-based access control",
            "Priority support",
            "Custom branding",
            "API access"
        ],
        "limits": {
            "users": 25,
            "incidents_per_month": 500,
            "storage_gb": 10
        }
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID"),
        "price": 299,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Unlimited users",
            "Advanced security features",
            "Custom integrations",
            "Dedicated support",
            "SLA guarantees",
            "On-premise option"
        ],
        "limits": {
            "users": -1,  # Unlimited
            "incidents_per_month": -1,  # Unlimited
            "storage_gb": 100
        }
    }
}

def create_customer(email: str, name: str) -> str:
    """Create a Stripe customer."""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"created_at": datetime.utcnow().isoformat()}
        )
        return customer.id
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create customer: {str(e)}"
        )

def create_subscription(customer_id: str, plan_id: str) -> Dict[str, Any]:
    """Create a subscription for a customer."""
    try:
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan ID"
            )
        
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": plan["price_id"]}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            metadata={
                "plan_id": plan_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create subscription: {str(e)}"
        )

def get_subscription(subscription_id: str) -> Dict[str, Any]:
    """Get subscription details."""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "plan_id": subscription.metadata.get("plan_id"),
            "customer_id": subscription.customer
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve subscription: {str(e)}"
        )

def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
    """Cancel a subscription."""
    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return {
            "id": subscription.id,
            "status": subscription.status,
            "cancel_at": subscription.cancel_at
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

def create_checkout_session(customer_id: str, plan_id: str, success_url: str, cancel_url: str) -> str:
    """Create a checkout session for subscription."""
    try:
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan ID"
            )
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": plan["price_id"],
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "plan_id": plan_id,
                "customer_id": customer_id
            }
        )
        
        return session.url
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create checkout session: {str(e)}"
        )

def create_billing_portal_session(customer_id: str, return_url: str) -> str:
    """Create a billing portal session for customer management."""
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        return session.url
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create billing portal session: {str(e)}"
        )

def get_usage_limits(plan_id: str) -> Dict[str, Any]:
    """Get usage limits for a plan."""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    return plan["limits"]

def check_usage_limit(plan_id: str, current_usage: Dict[str, int], resource: str) -> bool:
    """Check if usage is within plan limits."""
    limits = get_usage_limits(plan_id)
    limit = limits.get(resource, -1)
    
    if limit == -1:  # Unlimited
        return True
    
    current = current_usage.get(resource, 0)
    return current < limit

def get_plan_features(plan_id: str) -> List[str]:
    """Get features for a plan."""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        return []
    return plan["features"] 