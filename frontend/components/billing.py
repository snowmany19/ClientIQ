# frontend/components/billing.py

import streamlit as st
import requests
from typing import Dict, Any, List
import json
import os

# Use environment variable for API URL, fallback to localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

def get_auth_headers():
    """Get authentication headers for API requests."""
    token = st.session_state.get("token")
    if not token:
        st.error("No authentication token found. Please log in.")
        return None  # Don't stop, just return None
    
    return {"Authorization": f"Bearer {token}"}

def display_subscription_plans():
    """Display available subscription plans."""
    st.header("Available Plans")
    
    # Get plans from backend
    try:
        response = requests.get(f"{API_BASE_URL}/billing/plans", headers=get_auth_headers())
        if response.status_code == 200:
            plans = response.json()["plans"]
        else:
            st.error("Failed to load plans")
            return
    except Exception as e:
        st.error(f"Error loading plans: {str(e)}")
        return
    
    # Display plans in columns with card-like styling
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; background-color: #f8f9fa;">
            """, unsafe_allow_html=True)
            st.markdown("### Basic Plan")
            st.markdown(f"**${plans['basic']['price']}/month**")
            st.markdown("Perfect for single locations")
            
            st.markdown("**Features:**")
            for feature in plans['basic']['features']:
                st.markdown(f"• {feature}")
            
            if st.button("Subscribe to Basic", key="basic_sub_button", type="primary", use_container_width=True):
                create_checkout_session("basic")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div style="padding: 20px; border: 2px solid #007bff; border-radius: 10px; background-color: #f8f9fa; position: relative;">
            <div style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background-color: #007bff; color: white; padding: 5px 15px; border-radius: 15px; font-size: 12px;">MOST POPULAR</div>
            """, unsafe_allow_html=True)
            st.markdown("### Pro Plan")
            st.markdown(f"**${plans['pro']['price']}/month**")
            st.markdown("Ideal for multiple locations")
            
            st.markdown("**Features:**")
            for feature in plans['pro']['features']:
                st.markdown(f"• {feature}")
            
            if st.button("Subscribe to Pro", key="pro_sub_button", type="primary", use_container_width=True):
                create_checkout_session("pro")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div style="padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; background-color: #f8f9fa;">
            """, unsafe_allow_html=True)
            st.markdown("### Enterprise Plan")
            st.markdown(f"**${plans['enterprise']['price']}/month**")
            st.markdown("For large retail chains")
            
            st.markdown("**Features:**")
            for feature in plans['enterprise']['features']:
                st.markdown(f"• {feature}")
            
            if st.button("Subscribe to Enterprise", key="enterprise_sub_button", type="primary", use_container_width=True):
                create_checkout_session("enterprise")
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("**Need help choosing?** Contact our sales team for a custom plan tailored to your needs.")
    
    # Add Stripe badge
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <small style="color: #6c757d;">Secure checkout powered by Stripe</small>
    </div>
    """, unsafe_allow_html=True)

def create_checkout_session(plan_id: str):
    """Create a Stripe checkout session."""
    try:
        headers = get_auth_headers() or {}
        headers = {**headers, "Content-Type": "application/json"}
        response = requests.post(
            f"{API_BASE_URL}/billing/create-checkout-session",
            headers=headers,
            json={
                "plan_id": plan_id,
                "success_url": "http://localhost:8501/_billing_success_page",
                "cancel_url": "http://localhost:8501/_billing_cancel_page"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            checkout_url = data["checkout_url"]
            
            # Store checkout URL in session state
            st.session_state.stripe_checkout_url = checkout_url
            st.session_state.show_stripe_redirect = True
            
            st.success("Checkout session created successfully!")
            st.info("Click the button below to complete your purchase on Stripe.")
            
            # Use Streamlit's native link button for better UX
            st.link_button(
                "Complete Purchase on Stripe", 
                checkout_url, 
                type="primary",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("**What happens next:**")
            st.markdown("1. Click the button above to go to Stripe")
            st.markdown("2. Complete your payment on Stripe's secure checkout")
            st.markdown("3. You'll be redirected back to A.I.ncident - AI Incident Management Dashboard")
            st.markdown("4. Your subscription will be activated immediately")
            
        else:
            st.error(f"Failed to create checkout session: {response.status_code}")
            try:
                error_data = response.json()
                st.error(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                st.error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        st.error(f"Error creating checkout session: {str(e)}")

def display_my_subscription():
    """Display current user's subscription details."""
    st.header("My Subscription")
    
    try:
        response = requests.get(f"{API_BASE_URL}/billing/my-subscription", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            
            if data["subscription"] is None:
                st.info("No active subscription found.")
                st.markdown("### Get Started")
                st.info("**Switch to the 'Available Plans' tab to view subscription options.**")
                return
            
            subscription = data["subscription"]
            plan = data["plan"]
            features = data["features"]
            limits = data["limits"]
            
            # Subscription status with color coding
            status_color = {
                "active": "🟢",
                "past_due": "🟡",
                "canceled": "🔴",
                "incomplete": "🟡"
            }.get(subscription["status"], "⚪")
            
            st.markdown(f"**Status:** {status_color} {subscription['status'].title()}")
            
            # Plan details in a card-like container
            with st.container():
                st.markdown("""
                <div style="padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f8f9fa;">
                """, unsafe_allow_html=True)
                st.markdown(f"**Plan:** {plan['name']}")
                st.markdown(f"**Price:** ${plan['price']}/{plan['interval']}")
                
                # Billing period
                if subscription.get("current_period_start") and subscription.get("current_period_end"):
                    st.markdown("**Billing Period:**")
                    st.markdown(f"- Start: {subscription['current_period_start']}")
                    st.markdown(f"- End: {subscription['current_period_end']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Features
            st.markdown("**Features:**")
            for feature in features:
                st.markdown(f"• {feature}")
            
            # Limits
            st.markdown("**Limits:**")
            if limits["users"] == -1:
                st.markdown("• Unlimited users")
            else:
                st.markdown(f"• Up to {limits['users']} users")
            
            if limits["incidents_per_month"] == -1:
                st.markdown("• Unlimited incidents")
            else:
                st.markdown(f"• {limits['incidents_per_month']} incidents/month")
            
            st.markdown(f"• {limits['storage_gb']}GB storage")
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Manage Billing", key="manage_billing_button", use_container_width=True):
                    open_billing_portal()
            
            with col2:
                if st.button("Cancel Subscription", key="cancel_sub_button", type="secondary", use_container_width=True):
                    cancel_subscription()
        else:
            st.error("Failed to load subscription details")
    except Exception as e:
        st.error(f"Error loading subscription: {str(e)}")

def open_billing_portal():
    """Open Stripe billing portal."""
    try:
        response = requests.post(f"{API_BASE_URL}/billing/billing-portal", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            portal_url = data["portal_url"]
            
            st.success("Billing portal session created!")
            st.info("Click the button below to manage your billing on Stripe.")
            
            # Use Streamlit's native link button for better UX
            st.link_button(
                "Manage Billing on Stripe", 
                portal_url, 
                type="primary",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("**What you can do:**")
            st.markdown("1. Update payment methods")
            st.markdown("2. View billing history")
            st.markdown("3. Download invoices")
            st.markdown("4. Cancel subscription")
            
        else:
            st.error("Failed to open billing portal")
            try:
                error_data = response.json()
                st.error(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                st.error(f"HTTP {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error opening billing portal: {str(e)}")

def cancel_subscription():
    """Cancel current subscription."""
    if st.button("Confirm Cancellation", key="confirm_cancel_button", type="primary"):
        try:
            response = requests.post(f"{API_BASE_URL}/billing/cancel-subscription", headers=get_auth_headers())
            if response.status_code == 200:
                st.success("Subscription canceled successfully")
                st.rerun()
            else:
                st.error("Failed to cancel subscription")
        except Exception as e:
            st.error(f"Error canceling subscription: {str(e)}")

def display_usage_stats():
    """Display current usage statistics."""
    st.header("Usage Statistics")
    
    # Check if user is admin
    user_info = st.session_state.get("user")
    if user_info and user_info.get("role") == "admin":
        st.info("**Admin Access**: You have unlimited usage across all features!")
        
        # Show admin usage metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Incidents Created", "∞", "Unlimited")
            st.progress(0.0)  # No progress bar for unlimited
            st.caption("No limits")
        
        with col2:
            st.metric("Active Users", "∞", "Unlimited")
            st.progress(0.0)  # No progress bar for unlimited
            st.caption("No limits")
        
        with col3:
            st.metric("Current Plan", "Admin Premium", "Automatic")
            st.caption("Full system access")
        
        st.markdown("### Admin Capabilities")
        st.markdown("- **Unlimited incident reports** - No monthly limits on submissions")
        st.markdown("- **Full dashboard access** - View all incidents and analytics")
        st.markdown("- **All store access** - Submit incidents for any store location")
        st.markdown("- **Premium features** - Access to all current system features")
        
        st.markdown("---")
        st.markdown("### Future Admin Features")
        st.info("Future versions may include: User management, advanced reporting, system configuration, and billing oversight tools.")
        
        return
    
    try:
        response = requests.get(f"{API_BASE_URL}/billing/usage", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            usage = data["usage"]
            limits = data["limits"]
            plan_id = data["plan_id"]
            
            # Usage metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Incidents Created", usage["incidents"])
                if limits["incidents_per_month"] != -1:
                    st.progress(min(usage["incidents"] / limits["incidents_per_month"], 1.0))
                    st.caption(f"Limit: {limits['incidents_per_month']}")
            
            with col2:
                st.metric("Active Users", usage["users"])
                if limits["users"] != -1:
                    st.progress(min(usage["users"] / limits["users"], 1.0))
                    st.caption(f"Limit: {limits['users']}")
            
            with col3:
                st.metric("Current Plan", plan_id.title())
                st.caption("Subscription status")
            
            # Usage breakdown
            st.markdown("### Usage Breakdown")
            
            # Incidents by month (placeholder - would need actual data)
            st.markdown("**Recent Activity:**")
            st.info("Usage tracking will be implemented with actual incident data")
            
        else:
            st.error("Failed to load usage statistics")
    except Exception as e:
        st.error(f"Error loading usage stats: {str(e)}")

def billing_page():
    """Main billing page."""
    st.title("Billing & Subscription")
    
    # Reset plans shown state for fresh display
    if "plans_shown" in st.session_state:
        del st.session_state.plans_shown
    
    # Check if user is admin
    user_info = st.session_state.get("user")
    if user_info and user_info.get("role") == "admin":
        st.success("**Admin Access**: You have automatic premium access to all features!")
        st.info("As an administrator, you don't need to subscribe to any plan. You have full access to all A.I.ncident - AI Incident Management Dashboard features.")
        
        # Show admin features in card-like containers
        st.markdown("### Your Admin Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown("""
                <div style="padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f8f9fa;">
                """, unsafe_allow_html=True)
                st.markdown("**Full Dashboard Access**")
                st.markdown("- View all incident reports")
                st.markdown("- Access analytics and charts")
                st.markdown("- Filter and search incidents")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown("""
                <div style="padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f8f9fa;">
                """, unsafe_allow_html=True)
                st.markdown("**Incident Management**")
                st.markdown("- Submit unlimited incidents")
                st.markdown("- View incident details")
                st.markdown("- Download PDF reports")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            with st.container():
                st.markdown("""
                <div style="padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f8f9fa;">
                """, unsafe_allow_html=True)
                st.markdown("**System Access**")
                st.markdown("- Bypass subscription limits")
                st.markdown("- Access all store locations")
                st.markdown("- Full role-based permissions")
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Usage Overview")
        display_usage_stats()
        
        if st.button("Return to Dashboard", type="primary"):
            st.switch_page("dashboard.py")
        
        return
    
    # Check if user is employee (no billing access)
    if user_info and user_info.get("role") == "employee":
        st.warning("**Employee Access**: Billing is managed by your administrator.")
        st.info("Please contact your administrator for subscription and billing questions.")
        
        if st.button("Return to Dashboard", type="primary"):
            st.switch_page("dashboard.py")
        
        return
    
    # Staff users can access billing
    # Navigation tabs for staff users
    tab1, tab2, tab3 = st.tabs(["My Subscription", "Available Plans", "Usage Stats"])
    
    with tab1:
        display_my_subscription()
    
    with tab2:
        display_subscription_plans()
    
    with tab3:
        display_usage_stats()

def billing_success_page():
    """Page shown after successful subscription."""
    st.title("Subscription Successful!")
    st.success("Thank you for subscribing to A.I.ncident - AI Incident Management Dashboard!")
    
    st.markdown("### What's Next?")
    st.markdown("1. **Start Reporting Incidents** - Use the dashboard to create your first incident report")
    st.markdown("2. **Invite Team Members** - Add users to your organization")
    st.markdown("3. **Explore Features** - Check out all the features included in your plan")
    
    if st.button("Go to Dashboard", type="primary"):
        st.switch_page("dashboard.py")

def billing_cancel_page():
    """Page shown when subscription is canceled."""
    st.title("Subscription Canceled")
    st.warning("Your subscription was not completed.")
    
    st.markdown("### No worries!")
    st.markdown("You can still:")
    st.markdown("- Try a different plan")
    st.markdown("- Contact support for assistance")
    st.markdown("- Use the free trial features")
    
    if st.button("View Plans Again", type="primary"):
        st.switch_page("pages/billing.py") 