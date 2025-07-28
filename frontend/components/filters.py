import streamlit as st
import pandas as pd

# Predefined tags for HOA violations (matching backend FIXED_TAGS)
PREDEFINED_TAGS = [
    "Landscaping", "Trash", "Parking", "Exterior Maintenance", "Noise",
    "Pet Violation", "Architectural", "Pool/Spa", "Vehicle Storage",
    "Holiday Decorations", "Other", "Safety Hazard"
]

def apply_filters(incident_df: pd.DataFrame) -> pd.DataFrame:
    if incident_df.empty:
        st.warning("No incident data available for filtering.")
        return incident_df

    st.sidebar.header("Filter Incidents")

    # Optional: Clear filters button
    if st.sidebar.button("Clear All Filters"):
        st.session_state["filter_tags"] = []
        st.session_state["filter_severity"] = []
        st.session_state["filter_location"] = []

    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(incident_df['timestamp']):
        incident_df['timestamp'] = pd.to_datetime(incident_df['timestamp'], errors='coerce')

    # Date range (default to full range)
    min_date = incident_df['timestamp'].min().date()
    max_date = incident_df['timestamp'].max().date()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Normalize tags
    def parse_tags(t):
        if isinstance(t, list):
            return t
        elif isinstance(t, str):
            return [tag.strip() for tag in t.split(",") if tag.strip()]
        return []

    incident_df['tags'] = incident_df['tags'].apply(parse_tags)

    # Filter options - combine predefined tags with tags from data
    data_tags = {tag for tag_list in incident_df['tags'] for tag in tag_list}
    all_tags = sorted(set(PREDEFINED_TAGS + list(data_tags)))
    severity_options = sorted(incident_df['severity'].dropna().unique().tolist())
    location_options = sorted(incident_df['location'].dropna().unique().tolist())

    # Initialize session state once (no default= needed)
    if "filter_tags" not in st.session_state:
        st.session_state["filter_tags"] = []
    if "filter_severity" not in st.session_state:
        st.session_state["filter_severity"] = []
    if "filter_location" not in st.session_state:
        st.session_state["filter_location"] = []

    # Filters using session state
    selected_tags = st.sidebar.multiselect("Tags", options=all_tags, key="filter_tags")
    selected_severity = st.sidebar.multiselect("Severity", options=severity_options, key="filter_severity")
    selected_locations = st.sidebar.multiselect("Location", options=location_options, key="filter_location")

    # Start with full DataFrame
    filtered_df = incident_df.copy()

    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range)
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.date >= start_date.date()) &
            (filtered_df['timestamp'].dt.date <= end_date.date())
        ]

    if selected_tags:
        filtered_df = filtered_df[
            filtered_df['tags'].apply(lambda tags: any(tag in tags for tag in selected_tags))
        ]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)

    if selected_severity:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)

    if selected_locations:
        filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]
        if not isinstance(filtered_df, pd.DataFrame):
            filtered_df = pd.DataFrame(filtered_df)

    return filtered_df
