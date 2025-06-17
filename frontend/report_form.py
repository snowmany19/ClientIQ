import streamlit as st
import requests

def show_report_form():
    st.header("📋 Report New Incident")

    description = st.text_area("Incident Description", height=150)
    store = st.text_input("Store Name or ID")
    location = st.text_input("Location")
    offender = st.text_input("Offender (if known)")
    file = st.file_uploader("Upload Photo (optional)", type=["jpg", "jpeg", "png"])

    if st.button("Submit Incident"):
        with st.spinner("Submitting..."):
            from utils.api import submit_incident  # centralize request logic
            response = submit_incident(description, store, location, offender, file)

            if response and response.status_code == 200:
                result = response.json()
                st.success("Incident submitted successfully!")
                st.write("📝 Summary:", result.get("summary", "N/A"))
                st.write("🏷️ Tags:", result.get("tags", "N/A"))
                st.write("📄 PDF Path:", result.get("pdf_path", "N/A"))
            else:
                st.error("Failed to submit incident.")
                if response is not None:
                    st.json(response.json())
