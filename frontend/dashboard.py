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
st.set_page_config(page_title="A.I.ncident - AI Incident Management Dashboard", layout="wide")

# --- ROBUST LOGO PATH ---
LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "images", "ai_logo.png")

def get_base64_logo(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

from components.filters import apply_filters
from components.charts import render_charts
from components.incident_table import render_incident_table
from utils.api import get_jwt_token, get_user_info, submit_incident, get_accessible_stores, get_incidents_with_pagination, get_pagination_info, export_incidents_csv, get_dashboard_data

API_URL = "http://localhost:8000/api"

# -----------------------------------
# 🔐 Session Setup
# -----------------------------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "accessible_stores" not in st.session_state:
    st.session_state.accessible_stores = None
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
    st.session_state.accessible_stores = None
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
        
        incidents = dashboard_data.get("incidents", [])
        pagination = dashboard_data.get("pagination", {})
        accessible_stores = dashboard_data.get("accessible_stores", [])
        
        if not incidents:
            return pd.DataFrame(), None, pagination, accessible_stores
        
        df = pd.DataFrame(incidents)
        return df, None, pagination, accessible_stores
        
    except Exception as e:
        return pd.DataFrame(), f"Error fetching dashboard data: {str(e)}", None, None

# Legacy function for backward compatibility
@st.cache_data(ttl=30, show_spinner=True)
def fetch_incidents_with_pagination(token: str, page: int = 0, limit: int = 50):
    """Fetch incidents with pagination and error handling (legacy)."""
    if not token:
        return pd.DataFrame(), "No authentication token available"
    
    try:
        incidents = get_incidents_with_pagination(token, page * limit, limit)
        if incidents is None:
            return pd.DataFrame(), "Failed to fetch incidents"
        
        if not incidents:
            return pd.DataFrame(), None
        
        df = pd.DataFrame(incidents)
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Error fetching incidents: {str(e)}"

def handle_incident_fetch_error(error_msg: str):
    """Handle incident fetch errors, including 402 Payment Required."""
    if "Payment required" in error_msg or "402" in error_msg:
        st.error("Payment required. Please subscribe to continue using A.I.ncident - AI Incident Management Dashboard.")
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
        <h1 style="margin: 0; font-size: 2rem;">A.I.ncident - AI Incident Management Dashboard Login</h1>
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
        <strong>Secure AI-powered reporting. GDPR-aware. Modular backend. No PII stored by default.</strong>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ✅ Refresh user info after rerun
if st.session_state.token and st.session_state.user is None:
    user_obj = get_user_info(st.session_state.token)
    st.session_state.user = user_obj

    # 🔐 Check subscription status IMMEDIATELY after user info loads
    if user_obj:
        user_role = user_obj.get("role", "employee")
        subscription_status = user_obj.get("subscription_status", "inactive")
        
        # 🎯 Admins bypass billing - they always have full access
        if user_role == "admin":
            st.session_state.admin_bypass = True
        elif subscription_status not in ["active", "trialing"]:
            st.warning("Active subscription required to access A.I.ncident - AI Incident Management Dashboard.")
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

user_role = user.get("role", "employee")

# 🔐 RBAC: Define permissions based on role
if user_role == "admin":
    can_view_dashboard = True
    can_submit_incidents = True
    can_view_all_stores = True
    can_view_charts = True
    can_view_incident_log = True
elif user_role == "staff":
    can_view_dashboard = True
    can_submit_incidents = True
    can_view_all_stores = False
    can_view_charts = True
    can_view_incident_log = True
elif user_role == "employee":
    can_view_dashboard = False
    can_submit_incidents = True
    can_view_all_stores = False
    can_view_charts = False
    can_view_incident_log = False
else:
    # Default to most restrictive
    can_view_dashboard = False
    can_submit_incidents = True
    can_view_all_stores = False
    can_view_charts = False
    can_view_incident_log = False

# -----------------------------------
# 🎨 Dashboard Header
# -----------------------------------
# --- LOGO AND TITLE IN A BANNER AT TOP OF DASHBOARD ---
if st.session_state.token:
    logo_b64 = get_base64_logo(LOGO_PATH)
    st.markdown(
        f'''
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; margin-top: 1rem;">
            <img src="data:image/png;base64,{logo_b64}" width="180" style="margin-right: 32px;"/>
            <h1 style="margin: 0; font-size: 2.5rem;">A.I.ncident - AI Incident Management Dashboard</h1>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.caption(f"Last updated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
    st.caption(f"Logged in as **{user['username']}** ({user_role.capitalize()})")

# 🏬 Display store assignment
if user.get('store'):
    store_info = user['store']
    st.info(f"📍 **Store Assignment**: {store_info['store_number']} - {store_info['location']}")
elif user_role == "admin":
    st.info("👑 **Admin Access**: You can access all store locations")
else:
    st.warning("⚠️ **No Store Assignment**: Please contact your administrator to assign you to a store location.")

# 🎯 Show admin premium access indicator
if user_role == "admin":
    st.success("👑 **Admin Access**: You have automatic premium access to all features!")

# ✅ Fetch all dashboard data in a single optimized call
if st.session_state.token:
    incident_df, error, pagination_info, accessible_stores = fetch_dashboard_data(st.session_state.token, st.session_state.current_page)
    if error:
        handle_incident_fetch_error(error)
    else:
        # Update session state with fetched data
        if pagination_info is not None:
            st.session_state.pagination_info = pagination_info
        if accessible_stores is not None:
            st.session_state.accessible_stores = accessible_stores
else:
    incident_df = pd.DataFrame()
    st.error("❌ No authentication token available")

# 🛠️ Preprocess
if not incident_df.empty and 'tags' in incident_df.columns:
    incident_df['tags'] = incident_df['tags'].apply(
        lambda t: t if isinstance(t, list) else [tag.strip() for tag in str(t).split(",") if tag.strip()]
    )
if not incident_df.empty and 'timestamp' in incident_df.columns:
    incident_df['timestamp'] = pd.to_datetime(incident_df['timestamp'], errors="coerce")

# -----------------------------------
# 📊 Role-Based Dashboard
# -----------------------------------
if can_view_dashboard:
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        st.markdown("Filter and analyze incident patterns.")
        filtered_df = apply_filters(incident_df)

    # Show charts only to staff and admin
    if can_view_charts:
        with st.expander("📈 View Incident Trends", expanded=True):
            fig = render_charts(filtered_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    # Show incident log only to staff and admin
    if can_view_incident_log:
        st.subheader("📋 Incident Log")
        
        # Show pagination info
        if st.session_state.pagination_info:
            total = st.session_state.pagination_info.get("total", 0)
            pages = st.session_state.pagination_info.get("pages", 0)
            current_page = st.session_state.current_page + 1
            
            st.caption(f"📄 Showing page {current_page} of {pages} (Total: {total} incidents)")
        
        render_incident_table(filtered_df, user, st.session_state.token)
        
        # Pagination controls
        if st.session_state.pagination_info and st.session_state.pagination_info.get("pages", 0) > 1:
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button("⏮️ First", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page = 0
                    st.session_state.pagination_info = None  # Reset to refetch
                    st.rerun()
            
            with col2:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page = max(0, st.session_state.current_page - 1)
                    st.session_state.pagination_info = None  # Reset to refetch
                    st.rerun()
            
            with col3:
                if st.button("➡️ Next", disabled=st.session_state.current_page >= pages - 1):
                    st.session_state.current_page = min(pages - 1, st.session_state.current_page + 1)
                    st.session_state.pagination_info = None  # Reset to refetch
                    st.rerun()
            
            with col4:
                if st.button("⏭️ Last", disabled=st.session_state.current_page >= pages - 1):
                    st.session_state.current_page = pages - 1
                    st.session_state.pagination_info = None  # Reset to refetch
                    st.rerun()

    # After all sidebar filters are defined:
    if user and user.get("role") in ["admin", "staff"]:
        st.sidebar.markdown("---")
        if st.sidebar.button("Export Trends and Log", key="export_csv_btn_sidebar"):
            with st.spinner("Preparing CSV export..."):
                # Build filters from session state and widgets
                filters = {}
                # Date range
                date_range = st.session_state.get("Date Range")
                if date_range and len(date_range) == 2:
                    filters["start_date"] = str(date_range[0])
                    filters["end_date"] = str(date_range[1])
                # Tags, severity, location
                if st.session_state.get("filter_tags"):
                    filters["tag"] = ",".join(st.session_state["filter_tags"])
                if st.session_state.get("filter_severity"):
                    filters["severity"] = ",".join(str(s) for s in st.session_state["filter_severity"])
                if st.session_state.get("filter_location"):
                    filters["location"] = ",".join(st.session_state["filter_location"])
                export_incidents_csv(st.session_state.token, filters)
else:
    st.info("👤 **Employee View**: You can submit incidents but cannot view the dashboard. Contact your manager for access to incident reports and analytics.")

# -----------------------------------
# 🚨 Report Incident (All Roles)
# -----------------------------------
if can_submit_incidents:
    submitted = False
    res = None
    result = None

    with st.expander("🚨 Report New Incident"):
        with st.form("incident_form", clear_on_submit=True):
            st.markdown("Submit a new incident below. A summary and PDF report will be generated.")
            
            # Show role-based store restrictions
            if not can_view_all_stores:
                st.info("📍 **Store Restriction**: You can only submit incidents for your assigned store location.")
            
            col1, col2 = st.columns(2)
            with col1:
                # Show store selection based on user's accessible stores
                if st.session_state.accessible_stores:
                    if len(st.session_state.accessible_stores) == 1:
                        # User has only one store - auto-fill
                        store_name = st.text_input("🏬 Store", value=st.session_state.accessible_stores[0]["store_number"], disabled=True)
                        st.caption(f"📍 Assigned to: {st.session_state.accessible_stores[0]['store_number']} - {st.session_state.accessible_stores[0]['location']}")
                    else:
                        # User has multiple stores - show dropdown
                        store_options = [f"{store['store_number']} - {store['location']}" for store in st.session_state.accessible_stores]
                        selected_store = st.selectbox("🏬 Select Store", store_options)
                        # Extract store number from selection
                        store_name = selected_store.split(" - ")[0] if " - " in selected_store else selected_store
                else:
                    store_name = st.text_input("🏬 Store")
                
                location = st.text_input("Location")
                offender = st.text_input("Offender (if known)")

            with col2:
                description = st.text_area("Description", height=170)
                file = st.file_uploader("Upload Evidence Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("Submit Incident", type="primary")

    if submitted:
        with st.spinner("Submitting..."):
            token = st.session_state.get("token")
            if token and store_name:  # Add null checks
                res = submit_incident(token, description, store_name, location, offender, file)

                if res and res.status_code == 200:
                    result = res.json()
                    st.success("Incident submitted successfully!")

                    st.markdown(f"**Summary:** {result.get('summary', 'N/A')}")
                    st.markdown(f"**Tags:** {result.get('tags', 'N/A')}")
                    st.markdown(f"**Severity:** {result.get('severity', 'N/A')}")
                    st.markdown(f"**Reported By:** {result.get('reported_by', 'N/A')}")

                    pdf_url = f"http://localhost:8000/static/reports/{result.get('pdf_path', '').split('/')[-1]}"
                    try:
                        pdf_res = requests.get(pdf_url)
                        if pdf_res.status_code == 200:
                            st.markdown("### PDF Preview")
                            # Use st.download_button for PDF instead of iframe (Chrome blocks local PDFs)
                            st.download_button(
                                label="📄 Download Incident PDF",
                                data=pdf_res.content,
                                file_name=result.get("pdf_path", "incident.pdf").split("/")[-1],
                                mime="application/pdf"
                            )
                            st.info("PDF preview is disabled for security. Click the download button above to view the report.")
                        else:
                            st.warning("PDF not found.")
                    except Exception as e:
                        st.error(f"PDF fetch failed: {e}")
                else:
                    # Handle different error types
                    if res is None:
                        st.error("Failed to connect to server. Please check your connection.")
                    elif res.status_code == 400:
                        try:
                            error_data = res.json()
                            st.error(f"Validation Error: {error_data.get('detail', 'Invalid data provided')}")
                        except:
                            st.error("Invalid data provided. Please check your input.")
                    elif res.status_code == 403:
                        st.error("Access denied. You can only submit incidents for your assigned store.")
                    elif res.status_code == 401:
                        st.error("Authentication required. Please log in again.")
                        st.session_state.token = None
                        st.rerun()
                    elif res.status_code == 402:
                        st.error("Payment required. Please subscribe to continue using A.I.ncident - AI Incident Management Dashboard.")
                        st.info("Redirecting to billing page...")
                        st.switch_page("pages/billing.py")
                    elif res.status_code >= 500:
                        st.error("Server error. Please try again later.")
                    else:
                        st.error(f"Failed to submit incident. Status: {res.status_code}")
                        try:
                            st.json(res.json())
                        except:
                            st.text(res.text)
            else:
                st.error("Missing authentication token or store information.")



    if submitted and res and res.status_code == 200:
        # Clear cache and refresh data
        st.cache_data.clear()
        st.session_state.pagination_info = None
        st.button("🔄 Refresh Dashboard", on_click=st.rerun)

# Add refresh button in sidebar for all users
with st.sidebar:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.session_state.pagination_info = None
        st.rerun()

# Sidebar navigation and logout
with st.sidebar:
    st.title("A.I.ncident - AI Incident Management Dashboard")
    
    # User info section
    st.markdown("---")
    st.markdown(f"**👤 {user['username']}**")
    st.markdown(f"**🔑 {user_role.capitalize()}**")
    
    # Logout button
    if st.button("🚪 Logout", type="primary"):
        logout()
    
    st.markdown("---")
    
    nav_options = ["Dashboard", "Report Incident"]
    if user_role in ["admin", "staff"]:
        nav_options.append("Billing")
    if user_role in ["admin", "staff"]:
        nav_options.append("User Management")
    page = st.selectbox(
        "Navigation",
        nav_options,
        index=0
    )

# Page routing
if page == "Dashboard":
    # Current dashboard content (default view)
    pass
elif page == "Report Incident":
    # Show only the incident form
    st.title("🚨 Report New Incident")
    # The incident form is already in the main content area
elif page == "Billing":
    st.switch_page("pages/billing.py")
elif page == "User Management":
    # Import and show user management component
    from components.user_management import user_management_page
    user_management_page()













