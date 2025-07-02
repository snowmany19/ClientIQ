import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/api"

# Severity color mapping for numeric scores
def color_severity(val):
    try:
        score = int(val)
    except Exception:
        score = 1
    if score == 5:
        color = "#e74c3c"  # Red
    elif score == 4:
        color = "#f39c12"  # Orange
    elif score == 3:
        color = "#f7e967"  # Yellow
    elif score == 2:
        color = "#3498db"  # Blue
    elif score == 1:
        color = "#2ecc40"  # Green
    else:
        color = "white"
    return f"background-color: {color}; font-weight: bold;"

def render_incident_table(df: pd.DataFrame):
    if df.empty:
        st.info("No incidents to display.")
        return
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['timestamp_display'] = df['timestamp'].dt.strftime("%Y-%m-%d %H:%M")
    def parse_tags(t):
        if isinstance(t, list):
            return t
        elif isinstance(t, str):
            return [tag.strip() for tag in t.split(",") if tag.strip()]
        return []
    if 'tags' in df.columns:
        df['tags'] = df['tags'].apply(parse_tags)
    all_tags = sorted({tag for tag_list in df['tags'] for tag in tag_list}) if 'tags' in df.columns else []
    severity_options = sorted(df['severity'].dropna().unique().tolist()) if 'severity' in df.columns else []
    location_options = sorted(df['location'].dropna().unique().tolist()) if 'location' in df.columns else []
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_tags = st.multiselect("🏷️ Filter by Tags", options=all_tags, key="table_filter_tags")
    with col2:
        selected_severity = st.multiselect("🚨 Filter by Severity", options=severity_options, key="table_filter_severity")
    with col3:
        selected_locations = st.multiselect("📍 Filter by Location", options=location_options, key="table_filter_location")
    filtered_df = df.copy()
    if selected_tags and 'tags' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(tag in tags for tag in selected_tags))]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)
        filtered_df = filtered_df.copy()
    if selected_severity and 'severity' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)
        filtered_df = filtered_df.copy()
    if selected_locations and 'location' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)
        filtered_df = filtered_df.copy()
    if not isinstance(filtered_df, pd.DataFrame):
        filtered_df = pd.DataFrame(filtered_df)
    if filtered_df.empty:
        st.info("No incidents match the selected filters.")
        return
    # Display the table
    display_df = filtered_df.copy()
    if not isinstance(display_df, pd.DataFrame):
        display_df = pd.DataFrame(display_df)
    if 'tags' in display_df.columns:
        display_df['Tags'] = display_df['tags'].apply(lambda tags: ", ".join(tags) if isinstance(tags, list) else str(tags))
    display_df = display_df.rename(columns={
        'timestamp_display': 'Time',
        'severity': 'Severity',
        'location': 'Location',
        'description': 'Description',
        'summary': 'Summary',
        'reported_by': 'Reported By',
        'id': 'Incident ID'
    })
    columns_to_show = [c for c in ['Incident ID', 'Time', 'Tags', 'Severity', 'Location', 'Description', 'Summary', 'Reported By'] if c in display_df.columns]
    st.markdown("### 📋 Incident Log")
    # Always style Severity column
    styled_df = display_df[columns_to_show].style.map(color_severity, subset=['Severity'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    # Row selection via selectbox
    incident_ids = display_df['Incident ID'].tolist()
    selected_incident_id = st.selectbox("Select an incident to view PDF report:", incident_ids, format_func=lambda x: f"Incident {x}")
    selected_row = display_df[display_df['Incident ID'] == selected_incident_id].iloc[0]
    user_info = st.session_state.get("user")
    user_role = user_info.get("role", "employee") if user_info else "employee"
    # PDF Download/Open for staff/admin
    if user_role in ["admin", "staff"]:
        st.markdown("---")
        with st.expander("📄 Incident PDF Report", expanded=st.session_state.get(f"pdf_expanded_{selected_incident_id}", False)):
            check_key = f"check_pdf_{selected_incident_id}"
            if st.button("Check for PDF and Show Download Options", key=check_key):
                st.session_state[f"pdf_expanded_{selected_incident_id}"] = True
                pdf_url = f"{API_URL}/incidents/api/incident/{selected_incident_id}/pdf"
                token = st.session_state.get("token")
                headers = {"Authorization": f"Bearer {token}"}
                try:
                    r = requests.head(pdf_url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        st.info("Preview unavailable due to security. Please download.")
                        get_resp = requests.get(pdf_url, headers=headers)
                        if get_resp.status_code == 200:
                            st.download_button(
                                label="Download PDF",
                                data=get_resp.content,
                                file_name=f"incident_{selected_incident_id}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error("PDF could not be fetched for download.")
                    elif r.status_code == 404:
                        st.error(f"PDF not found for this incident (404). Please check if a PDF exists for this incident.")
                    else:
                        st.error(f"PDF Unavailable (URL: {pdf_url}, Status: {r.status_code})")
                except Exception as ex:
                    st.error(f"PDF Unavailable: {ex} (URL: {pdf_url})")
        # Delete Incident for staff/admin (only show when requested)
        if 'delete_pending_id' not in st.session_state:
            st.session_state['delete_pending_id'] = None
        if st.session_state['delete_pending_id'] == selected_incident_id:
            st.markdown("---")
            st.markdown(f"### 🗑️ Delete Incident {selected_incident_id} (Admin/Staff Only)")
            st.warning(f"Are you sure you want to delete Incident {selected_incident_id}? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Delete", key="confirm_delete_btn"):
                    token = st.session_state.get("token")
                    headers = {"Authorization": f"Bearer {token}"}
                    try:
                        resp = requests.delete(f"{API_URL}/incidents/{selected_incident_id}", headers=headers)
                        if resp.status_code == 200:
                            st.success("Incident deleted successfully!")
                            st.session_state['delete_pending_id'] = None
                            st.rerun()
                        else:
                            try:
                                st.error(resp.json().get("detail", "Failed to delete incident."))
                            except:
                                st.error("Failed to delete incident.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("Cancel Delete", key="cancel_delete_btn"):
                    st.session_state['delete_pending_id'] = None
                    st.info("Delete cancelled.")
        else:
            if st.button(f"Delete Incident {selected_incident_id}", key="show_delete_btn"):
                st.session_state['delete_pending_id'] = selected_incident_id




