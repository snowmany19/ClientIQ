# dashboard.py

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_extras.let_it_rain import rain
from streamlit.components.v1 import iframe

# ✅ MUST be first Streamlit call
st.set_page_config(page_title="IncidentIQ Dashboard", layout="wide")

from components.filters import apply_filters
from components.charts import render_charts
from components.incident_table import render_incident_table
from utils.api import get_jwt_token, get_user_info, submit_incident, get_accessible_stores, get_incidents_with_pagination, get_pagination_info

API_URL = "http://localhost:8000"

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

# -----------------------------------
# 📥 Fetch Incidents with Pagination
# -----------------------------------
@st.cache_data(ttl=60, show_spinner=True)
def fetch_incidents_with_pagination(token: str, page: int = 0, limit: int = 50):
    """Fetch incidents with pagination and error handling."""
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
        st.error("❌ Payment required. Please subscribe to continue using IncidentIQ.")
        st.info("Redirecting to billing page...")
        st.switch_page("pages/billing.py")
    else:
        st.error(f"❌ {error_msg}")

# -----------------------------------
# 🔐 Login Flow
# -----------------------------------
if not st.session_state.token:
    st.title("🔐 IncidentIQ Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            token = get_jwt_token(username, password)
            if token:
                st.session_state.token = token
                st.success("✅ Logged in successfully!")
                st.rerun()  # Refresh to load user info
            else:
                st.error("❌ Login failed. Please check your username and password.")

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
            st.warning("⚠️ Active subscription required to access IncidentIQ.")
            st.info("Please subscribe to continue using the platform.")
            if st.button("💳 Go to Billing"):
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
st.title("📊 IncidentIQ - Incident Management Dashboard")
st.caption(f"🕒 Last updated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
st.caption(f"👤 Logged in as **{user['username']}** ({user_role.capitalize()})")

# 🏬 Display store assignment
if user.get('store'):
    store_info = user['store']
    st.info(f"📍 **Store Assignment**: {store_info['name']} - {store_info['location']}")
elif user_role == "admin":
    st.info("👑 **Admin Access**: You can access all store locations")
else:
    st.warning("⚠️ **No Store Assignment**: Please contact your administrator to assign you to a store location.")

# 🎯 Show admin premium access indicator
if user_role == "admin":
    st.success("👑 **Admin Access**: You have automatic premium access to all features!")

# ✅ Fetch accessible stores for RBAC (only if subscription is active)
if st.session_state.token and st.session_state.accessible_stores is None:
    stores = get_accessible_stores(st.session_state.token)
    st.session_state.accessible_stores = stores

# Fetch pagination info (only if subscription is active)
if st.session_state.token and st.session_state.pagination_info is None:
    pagination_info = get_pagination_info(st.session_state.token)
    st.session_state.pagination_info = pagination_info

# Fetch incidents for current page (only if subscription is active)
if st.session_state.token:
    incident_df, error = fetch_incidents_with_pagination(st.session_state.token, st.session_state.current_page)
    if error:
        handle_incident_fetch_error(error)
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
        
        render_incident_table(filtered_df)
        
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
                        store_name = st.text_input("🏬 Store Name or ID", value=st.session_state.accessible_stores[0]["name"], disabled=True)
                        st.caption(f"📍 Assigned to: {st.session_state.accessible_stores[0]['name']}")
                    else:
                        # User has multiple stores - show dropdown
                        store_options = [store["name"] for store in st.session_state.accessible_stores]
                        selected_store = st.selectbox("🏬 Select Store", store_options)
                        store_name = selected_store
                else:
                    store_name = st.text_input("🏬 Store Name or ID")
                
                location = st.text_input("📍 Location")
                offender = st.text_input("🧍 Offender (if known)")

            with col2:
                description = st.text_area("📝 Description", height=170)
                file = st.file_uploader("📷 Upload Evidence Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("Submit Incident")

    if submitted:
        with st.spinner("Submitting..."):
            token = st.session_state.get("token")
            res = submit_incident(description, store_name, location, offender, file, token)

            if res and res.status_code == 200:
                result = res.json()
                st.success("✅ Incident submitted!")
                rain(emoji="📄", font_size=54, falling_speed=5, animation_length="infinite")

                st.markdown(f"**📝 Summary:** {result.get('summary', 'N/A')}")
                st.markdown(f"**🏷️ Tags:** {result.get('tags', 'N/A')}")
                st.markdown(f"**🔥 Severity:** {result.get('severity', 'N/A')}")
                st.markdown(f"**👤 Reported By:** {result.get('reported_by', 'N/A')}")

                pdf_url = f"{API_URL}/static/reports/{result.get('pdf_path', '').split('/')[-1]}"
                try:
                    pdf_res = requests.get(pdf_url)
                    if pdf_res.status_code == 200:
                        st.markdown("### 👀 PDF Preview")
                        # Use st.download_button for PDF instead of iframe (Chrome blocks local PDFs)
                        st.download_button(
                            label="📄 Download Incident PDF",
                            data=pdf_res.content,
                            file_name=result.get("pdf_path", "incident.pdf").split("/")[-1],
                            mime="application/pdf"
                        )
                        st.info("💡 PDF preview is disabled for security. Click the download button above to view the report.")
                    else:
                        st.warning("⚠️ PDF not found.")
                except Exception as e:
                    st.error(f"PDF fetch failed: {e}")
            else:
                # Handle different error types
                if res is None:
                    st.error("❌ Failed to connect to server. Please check your connection.")
                elif res.status_code == 400:
                    try:
                        error_data = res.json()
                        st.error(f"❌ Validation Error: {error_data.get('detail', 'Invalid data provided')}")
                    except:
                        st.error("❌ Invalid data provided. Please check your input.")
                elif res.status_code == 403:
                    st.error("❌ Access denied. You can only submit incidents for your assigned store.")
                elif res.status_code == 401:
                    st.error("❌ Authentication required. Please log in again.")
                    st.session_state.token = None
                    st.rerun()
                elif res.status_code == 402:
                    st.error("❌ Payment required. Please subscribe to continue using IncidentIQ.")
                    st.info("Redirecting to billing page...")
                    st.switch_page("pages/billing.py")
                elif res.status_code >= 500:
                    st.error("❌ Server error. Please try again later.")
                else:
                    st.error(f"❌ Failed to submit incident. Status: {res.status_code}")
                    try:
                        st.json(res.json())
                    except:
                        st.text(res.text)

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

# Sidebar navigation
with st.sidebar:
    st.title("🚨 IncidentIQ")
    
    # Role-based navigation
    if user_role == "admin":
        # Admin sees everything
        page = st.selectbox(
            "Navigation",
            ["Dashboard", "Report Incident", "Billing"],
            index=0
        )
    elif user_role == "staff":
        # Staff can access billing
        page = st.selectbox(
            "Navigation",
            ["Dashboard", "Report Incident", "Billing"],
            index=0
        )
    else:
        # Employees only see incident reporting
        page = st.selectbox(
            "Navigation",
            ["Dashboard", "Report Incident"],
            index=0
        )
    
    # User info
    st.markdown("---")
    if st.session_state.user:
        st.markdown(f"**User:** {st.session_state.user.get('username', 'Unknown')}")
        st.markdown(f"**Role:** {st.session_state.user.get('role', 'Unknown')}")
        
        # Show store assignment
        if st.session_state.user.get('store'):
            store_info = st.session_state.user['store']
            st.markdown(f"**🏬 Store:** {store_info['name']}")
            st.caption(f"📍 {store_info['location']}")
        elif user_role == "admin":
            st.markdown("**🏬 Store:** All Locations")
        else:
            st.markdown("**🏬 Store:** Not Assigned")
        
        # Show subscription status for staff
        if user_role in ["admin", "staff"]:
            subscription_status = st.session_state.user.get("subscription_status", "unknown")
            if user_role == "admin":
                st.markdown("**Status:** 👑 Admin Premium")
            elif subscription_status == "active":
                st.markdown("**Status:** ✅ Active Subscription")
            elif subscription_status == "trialing":
                st.markdown("**Status:** 🧪 Trial Active")
            else:
                st.markdown("**Status:** ❌ No Active Subscription")
    else:
        st.markdown("**User:** Unknown")
        st.markdown("**Role:** Unknown")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

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













