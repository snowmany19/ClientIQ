import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/api"

def render_incident_table(df: pd.DataFrame):
    #st.subheader("📋 Incident Log")

    if df.empty:
        st.info("No incidents to display.")
        return

    df = df.copy()

    # 🕒 Ensure timestamp is datetime and formatted
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['timestamp_display'] = df['timestamp'].dt.strftime("%Y-%m-%d %H:%M")

    # 🏷️ Ensure tags are lists
    def parse_tags(t):
        if isinstance(t, list):
            return t
        elif isinstance(t, str):
            return [tag.strip() for tag in t.split(",") if tag.strip()]
        return []

    df['tags'] = df['tags'].apply(parse_tags)

    # 🎯 Prepare filter options
    all_tags = sorted({tag for tag_list in df['tags'] for tag in tag_list})
    severity_options = sorted(df['severity'].dropna().unique().tolist())
    location_options = sorted(df['location'].dropna().unique().tolist())

    # 🎛️ Filters — default to none selected (show all)
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_tags = st.multiselect("Filter by Tags", options=all_tags, key="table_filter_tags")
    with col2:
        selected_severity = st.multiselect("Filter by Severity", options=severity_options, key="table_filter_severity")
    with col3:
        selected_locations = st.multiselect("Filter by Location", options=location_options, key="table_filter_location")

    # 🧮 Apply filters
    filtered_df = df.copy()

    if selected_tags:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(tag in tags for tag in selected_tags))]

    if selected_severity:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]

    if selected_locations:
        filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]

    # 🚨 Format severity with emojis
    def format_severity(sev):
        emojis = {
            "Low": "🟢 Low",
            "Medium": "🟡 Medium",
            "High": "🔴 High",
            "Critical": "⚠️ Critical"
        }
        return emojis.get(sev, sev)

    filtered_df['severity_display'] = filtered_df['severity'].apply(format_severity)
    filtered_df['tags'] = filtered_df['tags'].apply(lambda tags: ", ".join(tags) if isinstance(tags, list) else tags)

    # 📄 Columns to show
    display_columns = ['timestamp_display', 'tags', 'severity_display', 'location', 'description']
    column_renames = {
        'timestamp_display': '📅 Time',
        'tags': '🏷️ Tags',
        'severity_display': '🚨 Severity',
        'location': '📍 Location',
        'description': '📝 Description'
    }

    if 'summary' in filtered_df.columns:
        display_columns.append('summary')
        column_renames['summary'] = '🧠 Summary'

    # Add reported_by column if available
    if 'reported_by' in filtered_df.columns:
        display_columns.append('reported_by')
        column_renames['reported_by'] = '👤 Reported By'

    display_df = filtered_df[display_columns].rename(columns=column_renames)
    display_df = display_df.sort_values(by='📅 Time', ascending=False)

    # 📊 Show table
    st.dataframe(display_df, use_container_width=True, height=550)

    # 🗑️ Delete functionality for admin/staff
    user_info = st.session_state.get("user")
    user_role = user_info.get("role", "employee") if user_info else "employee"
    
    if user_role in ["admin", "staff"]:
        with st.expander("🗑️ Delete Incidents (Admin/Staff Only)", expanded=False):
            st.info("Select incidents to delete")
            
            # Create a list of incidents with checkboxes
            for idx, row in filtered_df.iterrows():
                incident_id = row.get('id')
                if incident_id:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['timestamp_display']}** - {row['location']} - {row['description'][:50]}...")
                    with col2:
                        if st.button(f"Delete", key=f"delete_incident_{incident_id}"):
                            st.session_state.delete_incident_id = incident_id
                            st.session_state.delete_incident_info = f"{row['timestamp_display']} - {row['location']}"

    # Delete confirmation
    if st.session_state.get("delete_incident_id"):
        incident_id = st.session_state.delete_incident_id
        incident_info = st.session_state.delete_incident_info
        
        st.warning(f"Are you sure you want to delete this incident?")
        st.info(f"Incident: {incident_info}")
        st.error("This action cannot be undone!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete"):
                token = st.session_state.get("token")
                headers = {"Authorization": f"Bearer {token}"}
                
                try:
                    resp = requests.delete(f"{API_URL}/incidents/{incident_id}", headers=headers)
                    if resp.status_code == 200:
                        st.success("Incident deleted successfully!")
                        st.session_state.delete_incident_id = None
                        st.session_state.delete_incident_info = None
                        st.rerun()
                    else:
                        try:
                            st.error(resp.json().get("detail", "Failed to delete incident."))
                        except:
                            st.error("Failed to delete incident.")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button("Cancel"):
                st.session_state.delete_incident_id = None
                st.session_state.delete_incident_info = None
                st.rerun()

    # ⬇️ CSV Export
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="incident_log.csv",
        mime="text/csv"
    )




