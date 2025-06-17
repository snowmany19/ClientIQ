# dashboard.py

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
from streamlit_extras.let_it_rain import rain
from streamlit.components.v1 import iframe


from components.filters import apply_filters
from components.charts import render_charts
from components.incident_table import render_incident_table
from utils.api import get_jwt_token, get_user_info, submit_incident

API_URL = "http://localhost:8000"

# -----------------------------------
# 🔐 Session Auth Setup
# -----------------------------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------------
# 🔐 Login Form
# -----------------------------------
if not st.session_state.token:
    st.set_page_config(page_title="IncidentIQ Login")
    st.title("🔐 IncidentIQ Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            token = get_jwt_token(username, password)
            if token:
                st.session_state.token = token
                st.session_state.user = get_user_info(token)
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    st.stop()

# -----------------------------------
# 👤 User Role Setup
# -----------------------------------
user = st.session_state.user
user_role = user.get("role", "employee") if user else "employee"
can_view_dashboard = user_role in ["admin", "manager"]
can_submit_incidents = True  # Everyone can submit

# -----------------------------------
# 🎨 Page Setup
# -----------------------------------
st.set_page_config(page_title="IncidentIQ Dashboard", layout="wide")
st.title("📊 IncidentIQ - Incident Management Dashboard")
st.caption(f"🕒 Last updated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
st.caption(f"👤 Logged in as **{user['username']}** ({user_role.capitalize()})")

# -----------------------------------
# 📥 Fetch Incidents
# -----------------------------------
@st.cache_data(ttl=60, show_spinner=True)
def fetch_incidents():
    try:
        res = requests.get(f"{API_URL}/incidents/")
        if res.status_code == 200:
            return pd.DataFrame(res.json())
        else:
            st.error("❌ Failed to load incidents.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error fetching incidents: {e}")
        return pd.DataFrame()

incident_df = fetch_incidents()

# 🛠️ Preprocess data
if 'tags' in incident_df.columns:
    incident_df['tags'] = incident_df['tags'].apply(
        lambda t: t if isinstance(t, list) else [tag.strip() for tag in str(t).split(",") if tag.strip()]
    )
if 'timestamp' in incident_df.columns:
    incident_df['timestamp'] = pd.to_datetime(incident_df['timestamp'], errors="coerce")

# -----------------------------------
# 📊 Dashboard Controls (Admin Only)
# -----------------------------------
if can_view_dashboard:
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        st.markdown("Filter and analyze incident patterns.")
        filtered_df = apply_filters(incident_df)

    with st.expander("📈 View Incident Trends", expanded=True):
        fig = render_charts(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Incident Log")
    render_incident_table(filtered_df)

# -----------------------------------
# 🚨 Report New Incident (All Roles)
# -----------------------------------
if can_submit_incidents:
    submitted = False
    res = None
    result = None

    with st.expander("🚨 Report New Incident"):
        with st.form("incident_form", clear_on_submit=True):
            st.markdown("Submit a new incident below. A summary and PDF report will be generated.")

            col1, col2 = st.columns(2)
            with col1:
                store_name = st.text_input("🏬 Store Name or ID")
                location = st.text_input("📍 Location")
                offender = st.text_input("🧍 Offender (if known)")

            with col2:
                description = st.text_area("📝 Description", height=170)
                file = st.file_uploader("📷 Upload Evidence Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("🚨 Submit Incident")

    # ✅ Post-form processing
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

                # 🧾 PDF preview & download
                pdf_url = f"{API_URL}/{result.get('pdf_path')}"
                try:
                    pdf_res = requests.get(pdf_url)
                    if pdf_res.status_code == 200:
                        from streamlit.components.v1 import iframe
                        st.markdown("### 👀 PDF Preview")
                        iframe(pdf_url, height=600, width=800)

                        st.download_button(
                            label="📄 Download Incident PDF",
                            data=pdf_res.content,
                            file_name=result.get("pdf_path", "incident.pdf").split("/")[-1],
                            mime="application/pdf"
                        )
                    else:
                        st.warning("⚠️ PDF not found.")
                except Exception as e:
                    st.error(f"PDF fetch failed: {e}")
            else:
                st.error("❌ Failed to submit.")
                if res:
                    st.json(res.json())
                else:
                    st.error("No response from server.")

    # 🔄 Optional Manual Refresh
    if submitted and res and res.status_code == 200:
        st.button("🔄 Refresh Dashboard", on_click=st.rerun)












