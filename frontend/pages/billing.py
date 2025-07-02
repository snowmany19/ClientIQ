# frontend/billing.py

import streamlit as st
from components.billing import billing_page

# Page configuration
st.set_page_config(
    page_title="Billing - A.I.ncident",
    page_icon="💳",
    layout="wide"
)

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.error("Please log in to access billing.")
    st.stop()

# Main billing page
billing_page() 