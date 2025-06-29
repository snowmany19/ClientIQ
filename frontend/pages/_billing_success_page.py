# frontend/billing_success.py

import streamlit as st
from components.billing import billing_success_page

# Page configuration
st.set_page_config(
    page_title="Subscription Success - A.I.ncident📊 - AI Incident Management Dashboard",
    page_icon="✅",
    layout="centered"
)

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.error("Please log in to access this page.")
    st.stop()

# Main success page
billing_success_page() 

st.title("✅ Subscription Successful!")
st.success("Thank you for subscribing to A.I.ncident📊 - AI Incident Management Dashboard!")

st.markdown("### What's Next?")
st.markdown("1. **Start Reporting Incidents** - Use the dashboard to create your first incident report")
st.markdown("2. **Invite Team Members** - Add users to your organization")
st.markdown("3. **Explore Features** - Check out all the features included in your plan")

if st.button("Go to Dashboard"):
    st.switch_page("dashboard.py") 