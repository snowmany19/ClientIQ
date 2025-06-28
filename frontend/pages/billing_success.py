# frontend/billing_success.py

import streamlit as st
from components.billing import billing_success_page

# Page configuration
st.set_page_config(
    page_title="Subscription Success - IncidentIQ",
    page_icon="✅",
    layout="wide"
)

# Success page
billing_success_page() 