# frontend/billing_cancel.py

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Subscription Canceled - A.I.ncident📊 - AI Incident Management Dashboard",
    page_icon="❌",
    layout="centered"
)

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.error("Please log in to access this page.")
    st.stop()

st.title("❌ Subscription Canceled")
st.warning("Your subscription was not completed.")

st.markdown("### No worries!")
st.markdown("You can still:")
st.markdown("- Try a different plan")
st.markdown("- Contact support for assistance")
st.markdown("- Use the free trial features")

if st.button("View Plans Again"):
    st.switch_page("pages/billing.py") 