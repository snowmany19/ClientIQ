# frontend/billing_cancel.py

import streamlit as st
from components.billing import billing_cancel_page

# Page configuration
st.set_page_config(
    page_title="Subscription Canceled - IncidentIQ",
    page_icon="❌",
    layout="wide"
)

# Cancel page
billing_cancel_page() 