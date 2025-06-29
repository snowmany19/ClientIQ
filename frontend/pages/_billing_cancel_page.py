# frontend/billing_cancel.py

import streamlit as st
from components.billing import billing_cancel_page

# Page configuration
st.set_page_config(
    page_title="Subscription Canceled - IncidentIQ",
    page_icon="❌",
    layout="wide"
)

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.error("Please log in to access this page.")
    st.stop()

# Main cancel page
billing_cancel_page() 