import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

API_URL = "http://localhost:8000/api"

def handle_api_error(response, operation: str) -> str:
    """Handle API errors and return user-friendly messages."""
    try:
        error_data = response.json()
        return error_data.get('detail', f'{operation} failed')
    except:
        return f'{operation} failed with status {response.status_code}'

def get_jwt_token(username: str, password: str) -> Optional[str]:
    """Get JWT token with error handling."""
    if not username or not password:
        st.error("Username and password are required.")
        return None
    
    try:
        res = requests.post(f"{API_URL}/login", data={
            "username": username,
            "password": password
        }, timeout=10)
        
        if res.status_code == 200:
            token = res.json().get("access_token")
            if token:
                return token
            else:
                st.error("No token received from server.")
                return None
        else:
            error_msg = handle_api_error(res, "Login")
            st.error(f"Login failed: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Login failed: Request timed out. Please check your connection.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Login failed: Cannot connect to server. Please check if the backend is running.")
        return None
    except Exception as e:
        st.error(f"Login failed: Unexpected error - {str(e)}")
        return None

def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """Get user information with error handling."""
    if not token:
        st.error("No token available. Please log in.")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/me", headers=headers, timeout=10)
        
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch user info")
            st.error(f"Failed to fetch user info: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("User info fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("User info fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        st.error(f"User info fetch failed: Unexpected error - {str(e)}")
        return None

def submit_incident(token: str, description: str, store: str, location: str, offender: str, file=None) -> Optional[requests.Response]:
    """Submit incident with comprehensive validation."""
    if not token:
        st.error("No token available. Please log in.")
        return None
    
    if not description or not store or not location:
        st.error("Missing required fields: description, store, and location are required.")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "description": description,
            "store": store,
            "location": location,
            "offender": offender
        }
        
        files = {}
        if file is not None:
            files["file"] = file
        
        res = requests.post(
            f"{API_URL}/incidents/",
            data=data,
            files=files,
            headers=headers,
            timeout=30
        )
        
        return res
        
    except requests.exceptions.Timeout:
        st.error("Incident submission failed: Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Incident submission failed: Cannot connect to server.")
        return None
    except Exception as e:
        st.error(f"Incident submission failed: Unexpected error - {str(e)}")
        return None

def get_accessible_stores(token: str) -> Optional[List[Dict[str, Any]]]:
    """Get accessible stores with error handling."""
    if not token:
        st.error("No token available. Please log in.")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/incidents/stores/accessible", headers=headers, timeout=10)
        
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch stores")
            st.error(f"Failed to fetch stores: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Store fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Store fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        st.error(f"Store fetch failed: Unexpected error - {str(e)}")
        return None

def get_incidents_with_pagination(token: str, skip: int = 0, limit: int = 50) -> Optional[list]:
    """Get incidents with pagination."""
    if not token:
        st.error("No token available. Please log in.")
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/incidents/?skip={skip}&limit={limit}", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 402:
            # Payment required - let the calling function handle the redirect
            return None
        else:
            error_msg = handle_api_error(res, "Fetch incidents")
            st.error(f"Failed to fetch incidents: {error_msg}")
            return None
    except requests.exceptions.Timeout:
        st.error("Incidents fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Incidents fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        st.error(f"Incidents fetch failed: Unexpected error - {str(e)}")
        return None

def get_pagination_info(token: str) -> Optional[Dict[str, Any]]:
    """Get pagination information."""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(f"{API_URL}/incidents/pagination-info", headers=headers, timeout=10)
        
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch pagination info")
            st.error(f"Failed to fetch pagination info: {error_msg}")
            return None
    except requests.exceptions.Timeout:
        st.error("Pagination info fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Pagination info fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        st.error(f"Pagination info fetch failed: Unexpected error - {str(e)}")
        return None

def export_incidents_csv(token, filters):
    """
    Export incidents as CSV using the current filters.
    Downloads the CSV file to the user's browser.
    """
    base_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")
    endpoint = f"{base_url}/api/incidents/export-csv"
    headers = {"Authorization": f"Bearer {token}", "accept": "text/csv"}
    params = urlencode(filters)
    url = f"{endpoint}?{params}" if params else endpoint
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        # Use Streamlit to trigger download
        st.download_button(
            label="Download CSV",
            data=response.content,
            file_name="incidents_export.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Failed to export CSV: {response.status_code} {response.text}")

