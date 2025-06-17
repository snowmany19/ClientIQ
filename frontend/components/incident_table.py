import streamlit as st
import pandas as pd

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

    display_df = filtered_df[display_columns].rename(columns=column_renames)
    display_df = display_df.sort_values(by='📅 Time', ascending=False)

    # 📊 Show table
    st.dataframe(display_df, use_container_width=True, height=550)

    # ⬇️ CSV Export
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="incident_log.csv",
        mime="text/csv"
    )




