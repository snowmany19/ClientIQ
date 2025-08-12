# backend/utils/stripe_utils.py
# Stripe integration utilities for ContractGuard.ai - AI Contract Review Platform

import os
import stripe
from typing import Dict, Any, Optional, List
from utils.logger import get_logger

logger = get_logger("stripe_utils")

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ===========================
# 💳 Subscription Plans
# ===========================

SUBSCRIPTION_PLANS = {
    "solo": {
        "name": "Solo",
        "price": 39,
        "currency": "usd",
        "interval": "month",
        "features": [
            "AI-powered contract analysis",
            "Risk assessment and scoring",
            "Contract summary generation",
            "Basic reporting",
            "Email support"
        ],
        "limits": {
            "contracts_per_month": 10,
            "users": 1,
            "storage_gb": 5,
            "workspaces": 1
        }
    },
    "team": {
        "name": "Team",
        "price": 99,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Everything in Solo",
            "Team collaboration",
            "Advanced risk analytics",
            "Custom risk scoring",
            "Priority support",
            "API access"
        ],
        "limits": {
            "contracts_per_month": 50,
            "users": 5,
            "storage_gb": 25,
            "workspaces": 3
        }
    },
    "business": {
        "name": "Business",
        "price": 299,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Everything in Team",
            "Multi-workspace management",
            "Advanced compliance tracking",
            "Custom integrations",
            "Dedicated account manager",
            "Training and onboarding"
        ],
        "limits": {
            "contracts_per_month": 250,
            "users": 20,
            "storage_gb": 100,
            "workspaces": 10
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 999,
        "currency": "usd",
        "interval": "month",
        "features": [
            "Everything in Business",
            "Unlimited contracts",
            "Custom AI model training",
            "Advanced security features",
            "24/7 phone support",
            "Custom SLA agreements"
        ],
        "limits": {
            "contracts_per_month": 1000,
            "users": 100,
            "storage_gb": 500,
            "workspaces": 50
        }
    }
}

def get_subscription_plans() -> Dict[str, Any]:
    """Get all available subscription plans."""
    return SUBSCRIPTION_PLANS

def get_plan_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific subscription plan by ID."""
    return SUBSCRIPTION_PLANS.get(plan_id)

def get_plan_features(plan_id: str) -> List[str]:
    """Get features for a specific plan."""
    plan = get_plan_by_id(plan_id)
    return plan.get("features", []) if plan else []

def get_plan_limits(plan_id: str) -> Dict[str, Any]:
    """Get limits for a specific plan."""
    plan = get_plan_by_id(plan_id)
    return plan.get("limits", {}) if plan else {}

# ===========================
# 🏢 Workspace Management
# ===========================

def create_workspace_subscription(
    workspace_id: str,
    plan_id: str,
    customer_email: str,
    customer_name: str
) -> Dict[str, Any]:
    """
    Create a new Stripe subscription for a workspace.
    
    Args:
        workspace_id: Unique workspace identifier
        plan_id: Subscription plan ID
        customer_email: Customer email address
        customer_name: Customer name
        
    Returns:
        Dictionary with subscription details
    """
    try:
        # Get plan details
        plan = get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan ID: {plan_id}")
        
        # Create or get customer
        customer = stripe.Customer.create(
            email=customer_email,
            name=customer_name,
            metadata={
                "workspace_id": workspace_id,
                "plan_id": plan_id
            }
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": plan_id}],
            metadata={
                "workspace_id": workspace_id,
                "plan_id": plan_id
            },
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"]
        )
        
        logger.info(f"Created subscription {subscription.id} for workspace {workspace_id}")
        
        return {
            "subscription_id": subscription.id,
            "customer_id": customer.id,
            "plan_id": plan_id,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None
        }
        
    except Exception as e:
        logger.error(f"Failed to create workspace subscription: {e}")
        raise

def update_workspace_subscription(
    subscription_id: str,
    new_plan_id: str
) -> Dict[str, Any]:
    """
    Update an existing workspace subscription.
    
    Args:
        subscription_id: Stripe subscription ID
        new_plan_id: New plan ID
        
    Returns:
        Updated subscription details
    """
    try:
        # Get current subscription
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription items
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription.items.data[0].id,
                "price": new_plan_id
            }],
            metadata={"plan_id": new_plan_id}
        )
        
        logger.info(f"Updated subscription {subscription_id} to plan {new_plan_id}")
        
        return {
            "subscription_id": updated_subscription.id,
            "plan_id": new_plan_id,
            "status": updated_subscription.status,
            "current_period_start": updated_subscription.current_period_start,
            "current_period_end": updated_subscription.current_period_end
        }
        
    except Exception as e:
        logger.error(f"Failed to update workspace subscription: {e}")
        raise

def cancel_workspace_subscription(
    subscription_id: str,
    cancel_at_period_end: bool = True
) -> Dict[str, Any]:
    """
    Cancel a workspace subscription.
    
    Args:
        subscription_id: Stripe subscription ID
        cancel_at_period_end: Whether to cancel at period end
        
    Returns:
        Cancellation details
    """
    try:
        if cancel_at_period_end:
            # Cancel at period end
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            message = "Subscription will be cancelled at the end of the current period"
        else:
            # Cancel immediately
            subscription = stripe.Subscription.cancel(subscription_id)
            message = "Subscription cancelled immediately"
        
        logger.info(f"Cancelled subscription {subscription_id}")
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "cancelled_at": subscription.cancelled_at,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel workspace subscription: {e}")
        raise

# ===========================
# 💰 Billing & Invoicing
# ===========================

def create_invoice(
    customer_id: str,
    amount: int,
    currency: str = "usd",
    description: str = "ContractGuard.ai subscription"
) -> Dict[str, Any]:
    """
    Create a Stripe invoice.
    
    Args:
        customer_id: Stripe customer ID
        amount: Amount in cents
        currency: Currency code
        description: Invoice description
        
    Returns:
        Invoice details
    """
    try:
        invoice = stripe.Invoice.create(
            customer=customer_id,
            amount=amount,
            currency=currency,
            description=description,
            auto_advance=True
        )
        
        logger.info(f"Created invoice {invoice.id} for customer {customer_id}")
        
        return {
            "invoice_id": invoice.id,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "status": invoice.status,
            "hosted_invoice_url": invoice.hosted_invoice_url
        }
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise

def get_customer_invoices(
    customer_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get invoices for a customer.
    
    Args:
        customer_id: Stripe customer ID
        limit: Maximum number of invoices to return
        
    Returns:
        List of invoice details
    """
    try:
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit
        )
        
        return [{
            "invoice_id": invoice.id,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "status": invoice.status,
            "created": invoice.created,
            "hosted_invoice_url": invoice.hosted_invoice_url
        } for invoice in invoices.data]
        
    except Exception as e:
        logger.error(f"Failed to get customer invoices: {e}")
        return []

# ===========================
# 🔐 Webhook Handling
# ===========================

def handle_webhook_event(
    event_type: str,
    event_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle Stripe webhook events.
    
    Args:
        event_type: Type of webhook event
        event_data: Event data from Stripe
        
    Returns:
        Processing result
    """
    try:
        if event_type == "invoice.payment_succeeded":
            return handle_payment_succeeded(event_data)
        elif event_type == "invoice.payment_failed":
            return handle_payment_failed(event_data)
        elif event_type == "customer.subscription.deleted":
            return handle_subscription_deleted(event_data)
        elif event_type == "customer.subscription.updated":
            return handle_subscription_updated(event_data)
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
            return {"status": "ignored", "event_type": event_type}
            
    except Exception as e:
        logger.error(f"Failed to handle webhook event {event_type}: {e}")
        return {"status": "error", "error": str(e)}

def handle_payment_succeeded(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle successful payment webhook."""
    try:
        invoice = event_data.get("data", {}).get("object", {})
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        
        logger.info(f"Payment succeeded for customer {customer_id}, subscription {subscription_id}")
        
        return {
            "status": "success",
            "event_type": "payment_succeeded",
            "customer_id": customer_id,
            "subscription_id": subscription_id
        }
        
    except Exception as e:
        logger.error(f"Failed to handle payment succeeded: {e}")
        return {"status": "error", "error": str(e)}

def handle_payment_failed(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle failed payment webhook."""
    try:
        invoice = event_data.get("data", {}).get("object", {})
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        
        logger.warning(f"Payment failed for customer {customer_id}, subscription {subscription_id}")
        
        return {
            "status": "success",
            "event_type": "payment_failed",
            "customer_id": customer_id,
            "subscription_id": subscription_id
        }
        
    except Exception as e:
        logger.error(f"Failed to handle payment failed: {e}")
        return {"status": "error", "error": str(e)}

def handle_subscription_deleted(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle subscription deletion webhook."""
    try:
        subscription = event_data.get("data", {}).get("object", {})
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        
        logger.info(f"Subscription deleted: {subscription_id} for customer {customer_id}")
        
        return {
            "status": "success",
            "event_type": "subscription_deleted",
            "customer_id": customer_id,
            "subscription_id": subscription_id
        }
        
    except Exception as e:
        logger.error(f"Failed to handle subscription deleted: {e}")
        return {"status": "error", "error": str(e)}

def handle_subscription_updated(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle subscription update webhook."""
    try:
        subscription = event_data.get("data", {}).get("object", {})
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        status = subscription.get("status")
        
        logger.info(f"Subscription updated: {subscription_id} for customer {customer_id}, status: {status}")
        
        return {
            "status": "success",
            "event_type": "subscription_updated",
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "new_status": status
        }
        
    except Exception as e:
        logger.error(f"Failed to handle subscription updated: {e}")
        return {"status": "error", "error": str(e)} 