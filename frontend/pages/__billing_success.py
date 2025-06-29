# frontend/billing_success.py

import streamlit as st
from components.billing import billing_success_page

# Page configuration
st.set_page_config(
    page_title="Subscription Success - IncidentIQ",
    page_icon="✅",
    layout="wide"
)

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.error("Please log in to access this page.")
    st.stop()

# Main success page
billing_success_page() 