import streamlit as st
import pandas as pd
import plotly.express as px

def render_charts(incident_df: pd.DataFrame):
    st.subheader("📈 Incident Trends")

    if incident_df.empty:
        st.warning("No incident data available.")
        return

    incident_df = incident_df.copy()  # avoid SettingWithCopyWarning

    # ✅ Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(incident_df['timestamp']):
        incident_df.loc[:, 'timestamp'] = pd.to_datetime(incident_df['timestamp'], errors='coerce')

    # 🗓 Date groupings
    incident_df.loc[:, 'date'] = incident_df['timestamp'].dt.date
    incident_df.loc[:, 'week'] = incident_df['timestamp'].dt.to_period("W").apply(lambda r: r.start_time.date())
    incident_df.loc[:, 'month'] = incident_df['timestamp'].dt.to_period("M").astype(str)

    # 🏷️ Ensure tags are clean
    def parse_tags(t):
        if isinstance(t, list):
            return t
        if isinstance(t, str):
            return [tag.strip() for tag in t.split(",") if tag.strip()]
        return []

    incident_df['tags'] = incident_df['tags'].fillna("").apply(parse_tags)

    # 🎛️ Optional tag filter (starts empty)
    all_tags = sorted({tag for tag_list in incident_df['tags'] for tag in tag_list})
    selected_tags = st.multiselect("Filter by tags", options=all_tags, key="charts_tag_filter")

    # 🔍 Apply filters only if selected
    filtered_df = incident_df.copy()
    if selected_tags:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(tag in tags for tag in selected_tags))]

    # 📊 Chart controls
    col1, col2 = st.columns(2)
    with col1:
        interval = st.selectbox("Group incidents by", ["Daily", "Weekly", "Monthly"], key="charts_interval")
    with col2:
        chart_type = st.radio("Chart type", ["Line Chart", "Bar Chart"], horizontal=True, key="charts_type")

    group_col = {"Daily": "date", "Weekly": "week", "Monthly": "month"}[interval]

    # 📈 Group and count
    trend_df = (
        filtered_df.groupby(group_col)
        .size()
        .reset_index(name="Incident Count")
        .sort_values(group_col)
    )

    if trend_df.empty:
        st.warning("No incidents to display in the selected timeframe.")
        return

    # 📉 Render chart
    if chart_type == "Line Chart":
        fig = px.line(trend_df, x=group_col, y="Incident Count", markers=True)
    else:
        fig = px.bar(trend_df, x=group_col, y="Incident Count")

    fig.update_layout(
        title=f"{interval} Incident Trends",
        xaxis_title=interval,
        yaxis_title="Incident Count",
        hovermode="x unified",
        template="plotly_white",
        height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
