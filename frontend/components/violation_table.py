import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from typing import Dict, Any
import base64
import json
import os

# Use environment variable for API URL, fallback to localhost for development
API_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

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
        color = "#FFD600"  # Darker Yellow
        return f"background-color: {color}; color: black; font-weight: bold; border: 2px solid black;"
    elif score == 2:
        color = "#3498db"  # Blue
    elif score == 1:
        color = "#2ecc40"  # Green
    else:
        color = "white"
    return f"background-color: {color}; font-weight: bold;"

def render_violation_table(df: pd.DataFrame, user: Dict[str, Any], token: str):
    """Render the violation table with interactive features."""
    
    if df.empty:
        st.info("No violations to display.")
        return
    
    # Prepare data for display
    display_df = df.copy()
    
    # Format timestamp
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Select columns to display
    columns_to_show = [
        'violation_number', 'timestamp', 'hoa_name', 'address', 'location', 
        'offender', 'status', 'repeat_offender_score', 'inspected_by'
    ]
    
    # Filter columns that exist in the dataframe
    available_columns = [col for col in columns_to_show if col in display_df.columns]
    
    # Rename columns for display
    column_mapping = {
        'violation_number': 'Violation #',
        'timestamp': 'Date',
        'hoa_name': 'HOA',
        'address': 'Address',
        'location': 'Location',
        'offender': 'Resident',
        'status': 'Status',
        'repeat_offender_score': 'Repeat Score',
        'inspected_by': 'Inspected By'
    }
    
    # Create display dataframe
    display_df = display_df[available_columns].copy()
    display_df.columns = [column_mapping.get(col, col) for col in available_columns]
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Add interactive features
    if len(display_df) > 0:
        st.subheader("📋 Violation Details")
        
        # Select a violation to view details
        selected_index = st.selectbox(
            "Select a violation to view details:",
            range(len(display_df)),
            format_func=lambda x: f"Violation #{display_df.iloc[x]['Violation #']} - {display_df.iloc[x]['Address']}"
        )
        
        if selected_index is not None:
            selected_violation = df.iloc[selected_index]
            display_violation_details(selected_violation, user, token)

def display_violation_details(violation: pd.Series, user: Dict[str, Any], token: str):
    """Display detailed information about a selected violation."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Violation Information")
        
        # Basic information
        info_data = {
            "Violation Number": violation.get('violation_number', 'N/A'),
            "Date": violation.get('timestamp', 'N/A'),
            "HOA": violation.get('hoa_name', 'N/A'),
            "Address": violation.get('address', 'N/A'),
            "Location": violation.get('location', 'N/A'),
            "Resident": violation.get('offender', 'N/A'),
            "Status": violation.get('status', 'open'),
            "Repeat Offender Score": violation.get('repeat_offender_score', 1),
            "Inspected By": violation.get('inspected_by', 'N/A'),
        }
        
        # Display info in a clean format
        for key, value in info_data.items():
            if key == "Repeat Offender Score":
                # Color code the repeat offender score
                score = int(value) if value is not None else 1
                if score >= 4:
                    st.markdown(f"**{key}:** 🔴 {score} (Chronic)")
                elif score >= 3:
                    st.markdown(f"**{key}:** 🟡 {score} (Pattern)")
                else:
                    st.markdown(f"**{key}:** 🟢 {score} (First-time)")
            elif key == "Status":
                # Color code the status
                status_colors = {
                    "open": "🔴",
                    "under_review": "🟡", 
                    "resolved": "🟢",
                    "disputed": "🟠"
                }
                status_value = str(value) if value is not None else "open"
                color = status_colors.get(status_value, "⚪")
                st.markdown(f"**{key}:** {color} {status_value.title()}")
            else:
                st.markdown(f"**{key}:** {value}")
        
        # Description and summary
        description = violation.get('description')
        if description and str(description).strip():
            st.markdown("### Description")
            st.text(str(description))
        
        summary = violation.get('summary')
        if summary and str(summary).strip():
            st.markdown("### AI Summary")
            st.text(str(summary))
        
        # Tags
        tags = violation.get('tags')
        if tags:
            st.markdown("### Tags")
            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            elif isinstance(tags, list):
                tag_list = [str(tag).strip() for tag in tags if tag]
            else:
                tag_list = [str(tags).strip()]
            
            for tag in tag_list:
                st.markdown(f"• {tag}")
    
    with col2:
        st.markdown("### Actions")
        
        # View PDF
        pdf_path = violation.get('pdf_path')
        if pdf_path and str(pdf_path).strip():
            if st.button("📄 Download PDF Report", type="primary"):
                view_pdf(str(pdf_path), token)
        
        # View Image
        image_url = violation.get('image_url')
        if image_url and str(image_url).strip():
            if st.button("🖼️ View Image"):
                view_image(str(image_url))
        
        # Status Management
        st.markdown("---")
        st.markdown("### Status Management")
        
        # Status update form
        with st.form(key=f"status_form_{violation.get('id', 'unknown')}"):
            new_status = st.selectbox(
                "Update Status",
                ["open", "under_review", "resolved", "disputed"],
                format_func=get_status_label,
                key=f"status_{violation.get('id', 'unknown')}"
            )
            
            resolution_notes = ""
            resolved_by = ""
            
            if new_status == "resolved":
                resolution_notes = st.text_area(
                    "Resolution Notes",
                    placeholder="Describe how the violation was resolved...",
                    key=f"notes_{violation.get('id', 'unknown')}"
                )
                resolved_by = st.text_input(
                    "Resolved By",
                    placeholder="Name of person who resolved it",
                    key=f"resolved_by_{violation.get('id', 'unknown')}"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update Status"):
                    violation_id = int(violation.get('id', 0))
                    success, result = update_violation_status(
                        violation_id, 
                        new_status, 
                        token, 
                        resolution_notes, 
                        resolved_by
                    )
                    
                    if success:
                        st.success("✅ Status updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update status: {result}")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    pass
        
        # Delete violation (admin and HOA board only)
        user_role = user.get('role', 'inspector')
        if user_role in ['admin', 'hoa_board']:
            st.markdown("---")
            violation_id = violation.get('id')
            if violation_id is not None:
                if st.button("🗑️ Delete Violation", type="secondary"):
                    delete_violation(int(violation_id), token)

def view_pdf(pdf_path: str, token: str):
    """Download PDF with clear viewing instructions."""
    try:
        # Extract violation ID from PDF path
        if '_' in pdf_path:
            violation_id = pdf_path.split('_')[1]
        else:
            # Try to extract from the full path
            violation_id = pdf_path.split('/')[-1].replace('.pdf', '')
        
        st.info(f"Loading PDF for violation {violation_id}")
        
        # Construct PDF URL
        pdf_url = f"{API_URL}/violations/{violation_id}/pdf"
        
        # Make request to get PDF
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(pdf_url, headers=headers)
        
        if response.status_code == 200:
            # Get file size in KB
            file_size_kb = len(response.content) / 1024
            
            st.success(f"✅ PDF loaded successfully! ({file_size_kb:.1f} KB)")
            
            # Download button
            st.download_button(
                label="📥 Download PDF Report",
                data=response.content,
                file_name=f"violation_{violation_id}.pdf",
                mime="application/pdf"
            )
            
            st.info("""
            **📋 How to view the PDF:**
            1. Click the download button above
            2. Open the downloaded file with any PDF viewer
            3. The report contains all violation details and photos
            """)
            
        else:
            st.error(f"❌ Failed to load PDF (Status: {response.status_code})")
            st.error("Please check your connection or contact support.")
            
    except Exception as e:
        st.error(f"❌ Error loading PDF: {str(e)}")

def view_image(image_path: str):
    """View violation image."""
    try:
        if image_path and image_path.startswith('static/'):
            # For local images, try to display directly
            st.image(image_path, caption="Violation Image", use_column_width=True)
        else:
            st.info("Image not available for display.")
    except Exception as e:
        st.error(f"Error viewing image: {e}")

def delete_violation(violation_id: int, token: str):
    """Delete a violation."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f"{API_URL}/violations/{violation_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            st.success("Violation deleted successfully!")
            st.rerun()
        else:
            st.error(f"Failed to delete violation: {response.status_code}")
    except Exception as e:
        st.error(f"Error deleting violation: {e}")

def get_status_color(status: str) -> str:
    """Get color for status badge."""
    status_colors = {
        "open": "🔴",
        "under_review": "🟡", 
        "resolved": "🟢",
        "disputed": "🟠"
    }
    return status_colors.get(status, "⚪")

def get_status_label(status: str) -> str:
    """Get human-readable status label."""
    status_labels = {
        "open": "Open",
        "under_review": "Under Review",
        "resolved": "Resolved",
        "disputed": "Disputed"
    }
    return status_labels.get(status, status.title())

def update_violation_status(violation_id: int, new_status: str, token: str, resolution_notes: str = "", resolved_by: str = ""):
    """Update violation status via API."""
    try:
        # Build URL with query parameters
        params = {"new_status": new_status}
        if resolution_notes:
            params["resolution_notes"] = resolution_notes
        if resolved_by:
            params["resolved_by"] = resolved_by
            
        url = f"{API_URL}/violations/{violation_id}/status"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.put(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Legacy function for backward compatibility
def render_incident_table(df: pd.DataFrame, user: Dict[str, Any], token: str):
    """Legacy function - use render_violation_table instead."""
    return render_violation_table(df, user, token)




