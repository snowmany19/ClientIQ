# dashboard.py

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

from streamlit.components.v1 import iframe
from PIL import Image
import os
import base64
import time

# ✅ MUST be first Streamlit call
st.set_page_config(page_title="CivicLogHOA - HOA Violation Management Dashboard", layout="wide")

# --- ROBUST LOGO PATH ---
LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "images", "ai_logo.png")

def get_base64_logo(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

from components.filters import apply_filters
from components.charts import render_charts
from components.violation_table import render_violation_table
from utils.api import get_jwt_token, get_user_info, submit_violation, get_accessible_hoas, get_violations_with_pagination, get_pagination_info, export_violations_csv, get_dashboard_data

# Use environment variable for API URL, fallback to localhost for development
API_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# -----------------------------------
# 🔐 Session Setup
# -----------------------------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "accessible_hoas" not in st.session_state:
    st.session_state.accessible_hoas = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "pagination_info" not in st.session_state:
    st.session_state.pagination_info = None


# --- LOGO IN SIDEBAR ---
with st.sidebar:
    st.image(LOGO_PATH, width=40)

# -----------------------------------
# 🔐 Logout Function
# -----------------------------------
def logout():
    """Clear session state and return to login."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.accessible_hoas = None
    st.session_state.current_page = 0
    st.session_state.pagination_info = None

    st.rerun()

# -----------------------------------
# 📥 Fetch Dashboard Data (Optimized)
# -----------------------------------
@st.cache_data(ttl=30, show_spinner=True)
def fetch_dashboard_data(token: str, page: int = 0, limit: int = 50):
    """Fetch all dashboard data in a single optimized call."""
    if not token:
        return pd.DataFrame(), "No authentication token available", None, None
    
    try:
        dashboard_data = get_dashboard_data(token, page * limit, limit)
        if dashboard_data is None:
            return pd.DataFrame(), "Failed to fetch dashboard data", None, None
        
        violations = dashboard_data.get("violations", [])
        pagination = dashboard_data.get("pagination", {})
        accessible_hoas = dashboard_data.get("accessible_hoas", [])
        
        if not violations:
            return pd.DataFrame(), None, pagination, accessible_hoas
        
        df = pd.DataFrame(violations)
        return df, None, pagination, accessible_hoas
        
    except Exception as e:
        return pd.DataFrame(), f"Error fetching dashboard data: {str(e)}", None, None

# Legacy function for backward compatibility
@st.cache_data(ttl=30, show_spinner=True)
def fetch_violations_with_pagination(token: str, page: int = 0, limit: int = 50):
    """Fetch violations with pagination and error handling (legacy)."""
    if not token:
        return pd.DataFrame(), "No authentication token available"
    
    try:
        violations = get_violations_with_pagination(token, page * limit, limit)
        if violations is None:
            return pd.DataFrame(), "Failed to fetch violations"
        
        if not violations:
            return pd.DataFrame(), None
        
        df = pd.DataFrame(violations)
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Error fetching violations: {str(e)}"

def handle_violation_fetch_error(error_msg: str):
    """Handle violation fetch errors, including 402 Payment Required."""
    if "Payment required" in error_msg or "402" in error_msg:
        st.error("Payment required. Please subscribe to continue using CivicLogHOA - HOA Violation Management Dashboard.")
        st.info("Redirecting to billing page...")
        st.switch_page("pages/billing.py")
    else:
        st.error(f"{error_msg}")

# -----------------------------------
# 🔐 Login Flow
# -----------------------------------
if not st.session_state.token:
    # Centered logo and title above login form
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="data:image/png;base64,{}" width="250" style="margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2rem;">CivicLogHOA - HOA Violation Management Dashboard Login</h1>
    </div>
    """.format(get_base64_logo(LOGO_PATH)), unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")

        if submitted:
            token = get_jwt_token(username, password)
            if token:
                st.session_state.token = token
                st.success("Logged in successfully!")
                st.rerun()  # Refresh to load user info
            else:
                st.error("Login failed. Please check your username and password.")

    # Forgot password button below the form
    st.markdown("---")
    if st.button("Forgot Password?", type="secondary"):
        st.info("Please contact your administrator to reset your password.")
    
    # Security statement at the bottom
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #6c757d; font-size: 14px;">
        <strong>Secure AI-powered HOA violation tracking. GDPR-aware. Modular backend. No PII stored by default.</strong>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ✅ Refresh user info after rerun
if st.session_state.token and st.session_state.user is None:
    user_obj = get_user_info(st.session_state.token)
    st.session_state.user = user_obj

    # 🔐 Check subscription status IMMEDIATELY after user info loads
    if user_obj:
        user_role = user_obj.get("role", "inspector")
        subscription_status = user_obj.get("subscription_status", "inactive")
        
        # 🎯 Admins bypass billing - they always have full access
        if user_role == "admin":
            st.session_state.admin_bypass = True
        elif subscription_status not in ["active", "trialing"]:
            st.warning("Active subscription required to access CivicLogHOA - HOA Violation Management Dashboard.")
            st.info("Please subscribe to continue using the platform.")
            if st.button("Go to Billing", type="primary"):
                st.switch_page("pages/billing.py")
            st.stop()

# -----------------------------------
# 👤 User Info & RBAC
# -----------------------------------
user = st.session_state.user
if not user or "username" not in user:
    st.warning("⚠️ User info not loaded. Please try logging in again.")
    st.stop()

user_role = user.get("role", "inspector")

# 🔐 RBAC: Define permissions based on role
if user_role == "admin":
    can_view_dashboard = True
    can_submit_violations = True
    can_view_all_hoas = True
    can_view_charts = True
    can_view_violation_log = True
elif user_role == "hoa_board":
    can_view_dashboard = True
    can_submit_violations = True
    can_view_all_hoas = False
    can_view_charts = True
    can_view_violation_log = True
elif user_role == "inspector":
    can_view_dashboard = True
    can_submit_violations = True
    can_view_all_hoas = False
    can_view_charts = True
    can_view_violation_log = True
else:
    can_view_dashboard = False
    can_submit_violations = False
    can_view_all_hoas = False
    can_view_charts = False
    can_view_violation_log = False

# -----------------------------------
# 🎯 Main Dashboard
# -----------------------------------
if can_view_dashboard:
    # Header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏘️ CivicLogHOA - HOA Violation Management Dashboard")
        st.markdown(f"**Welcome, {user.get('username', 'User')}** ({user_role.title()})")
    with col2:
        if user.get("hoa"):
            st.info(f"HOA: {user['hoa']['name']}")
    with col3:
        if st.button("Logout", type="secondary"):
            logout()

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 Submit Violation", "📋 Violation Log", "💳 Billing"])

    # -----------------------------------
    # 📊 Dashboard Tab
    # -----------------------------------
    with tab1:
        if can_view_charts:
            st.header("📊 Violation Analytics")
            
            # Fetch data
            df, error, pagination, accessible_hoas = fetch_dashboard_data(st.session_state.token, st.session_state.current_page)
            
            if error:
                handle_violation_fetch_error(error)
            elif not df.empty:
                # Display charts
                render_charts(df)
                
                # Quick stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Violations", len(df))
                with col2:
                    open_violations = len(df[df.get('status', 'open') == 'open'])
                    st.metric("Open Violations", open_violations)
                with col3:
                    avg_score = df.get('repeat_offender_score', pd.Series([1])).mean()
                    st.metric("Avg Repeat Score", f"{avg_score:.1f}")
                with col4:
                    unique_addresses = df.get('address', pd.Series()).nunique()
                    st.metric("Properties", unique_addresses)
            else:
                st.info("No violation data available.")

    # -----------------------------------
    # 📝 Submit Violation Tab
    # -----------------------------------
    with tab2:
        if can_submit_violations:
            st.header("📝 Submit New Violation")
            
            # Get accessible HOAs
            if st.session_state.accessible_hoas is None:
                accessible_hoas = get_accessible_hoas(st.session_state.token)
                st.session_state.accessible_hoas = accessible_hoas
            
            if st.session_state.accessible_hoas:
                with st.form("violation_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # HOA selection
                        hoa_options = [f"{hoa['hoa_number']} - {hoa['name']}" for hoa in st.session_state.accessible_hoas]
                        selected_hoa = st.selectbox("HOA", hoa_options)
                        
                        # Address field
                        address = st.text_input("Property Address/Unit #", placeholder="e.g., 123 Main St, Unit 4A")
                        
                        # Location within property
                        location = st.text_input("Specific Location", placeholder="e.g., Front yard, Back patio")
                        
                        # Resident information
                        offender = st.text_input("Resident Information", placeholder="e.g., John Smith or Unit 4A resident")
                    
                    with col2:
                        # GPS coordinates (optional)
                        gps_coordinates = st.text_input("GPS Coordinates (Optional)", placeholder="e.g., 37.7749,-122.4194")
                        
                        # Violation type
                        violation_types = [
                            "Landscaping", "Trash", "Parking", "Exterior Maintenance", "Noise",
                            "Pet Violation", "Architectural", "Pool/Spa", "Vehicle Storage",
                            "Holiday Decorations", "Safety Hazard", "Other"
                        ]
                        violation_type = st.selectbox("Violation Type", ["Select type..."] + violation_types)
                        
                        # Status
                        status = st.selectbox("Status", ["open", "under_review", "resolved", "disputed"])
                        
                        # File upload
                        uploaded_file = st.file_uploader("Upload Photo (Optional)", type=['jpg', 'jpeg', 'png'])
                    
                    # Description
                    description = st.text_area("Violation Description", 
                                             placeholder="Describe the violation in detail...",
                                             height=150)
                    
                    submitted = st.form_submit_button("Submit Violation", type="primary")
                    
                    if submitted:
                        if not description or not selected_hoa or not address or not location or not offender:
                            st.error("Please fill in all required fields.")
                        elif violation_type == "Select type...":
                            st.error("Please select a violation type.")
                        else:
                            # Extract HOA number from selection
                            hoa_number = selected_hoa.split(" - ")[0]
                            
                            # Submit violation
                            response = submit_violation(
                                st.session_state.token,
                                description=description,
                                hoa=hoa_number,
                                address=address,
                                location=location,
                                offender=offender,
                                gps_coordinates=gps_coordinates if gps_coordinates else None,
                                violation_type=violation_type,
                                file=uploaded_file
                            )
                            
                            if response and response.status_code == 200:
                                st.success("Violation submitted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to submit violation. Please try again.")
            else:
                st.warning("No HOAs assigned to your account.")
        else:
            st.warning("You don't have permission to submit violations.")

    # -----------------------------------
    # 📋 Violation Log Tab
    # -----------------------------------
    with tab3:
        if can_view_violation_log:
            st.header("📋 Violation Log")
            
            # Fetch data
            df, error, pagination, accessible_hoas = fetch_dashboard_data(st.session_state.token, st.session_state.current_page)
            
            if error:
                handle_violation_fetch_error(error)
            elif not df.empty:
                # Display violation table
                render_violation_table(df, user, st.session_state.token)
                
                # Pagination controls
                if pagination and pagination.get("pages", 0) > 1:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        if st.button("← Previous") and st.session_state.current_page > 0:
                            st.session_state.current_page -= 1
                            st.rerun()
                    with col2:
                        st.write(f"Page {st.session_state.current_page + 1} of {pagination.get('pages', 1)}")
                    with col3:
                        if st.button("Next →") and st.session_state.current_page < pagination.get("pages", 1) - 1:
                            st.session_state.current_page += 1
                            st.rerun()
            else:
                st.info("No violations to display.")
        else:
            st.warning("You don't have permission to view the violation log.")

    # -----------------------------------
    # 💳 Billing Tab
    # -----------------------------------
    with tab4:
        st.header("💳 Billing & Subscription")
        st.info("Manage your subscription and billing information.")
        if st.button("Go to Billing Page", type="primary"):
            st.switch_page("pages/billing.py")

else:
    st.error("Access denied. You don't have permission to view the dashboard.")













