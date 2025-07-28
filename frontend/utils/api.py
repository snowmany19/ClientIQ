import requests
import streamlit as st
from typing import Optional, List, Dict, Any
import pandas as pd
from urllib.parse import urlencode
import os

# Read API_BASE_URL from environment variable, fallback to localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

def handle_api_error(response, operation: str) -> str:
    """Handle API errors and return user-friendly messages."""
    try:
        error_data = response.json()
        return error_data.get('detail', f'{operation} failed')
    except:
        return f'{operation} failed with status {response.status_code}'

def get_jwt_token(username: str, password: str) -> Optional[str]:
    """Get JWT token for authentication."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """Get current user information."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to get user info: {e}")
        return None

def submit_violation(token: str, description: str, hoa: str, address: str, location: str, 
                    offender: str, gps_coordinates: Optional[str] = None, 
                    violation_type: Optional[str] = None, file: Optional[Any] = None) -> Optional[requests.Response]:
    """Submit a new violation."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        data = {
            "description": description,
            "hoa": hoa,
            "address": address,
            "location": location,
            "offender": offender,
        }
        
        if gps_coordinates:
            data["gps_coordinates"] = gps_coordinates
        if violation_type:
            data["violation_type"] = violation_type
        
        files = {}
        if file:
            files["file"] = file
        
        response = requests.post(
            f"{API_BASE_URL}/violations/",
            data=data,
            files=files,
            headers=headers
        )
        return response
    except Exception as e:
        st.error(f"Failed to submit violation: {e}")
        return None

def get_accessible_hoas(token: str) -> List[Dict[str, Any]]:
    """Get HOAs accessible to the current user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/violations/hoas/accessible", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Failed to get accessible HOAs: {e}")
        return []

def get_violations_with_pagination(token: str, skip: int = 0, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Get violations with pagination."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/violations/",
            params={"skip": skip, "limit": limit},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to get violations: {e}")
        return None

def get_pagination_info(token: str) -> Optional[Dict[str, Any]]:
    """Get pagination information for violations."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/violations/pagination-info", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to get pagination info: {e}")
        return None

def export_violations_csv(token: str, filters: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
    """Export violations to CSV."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = filters or {}
        response = requests.get(
            f"{API_BASE_URL}/violations/export-csv",
            params=params,
            headers=headers
        )
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.error(f"Failed to export violations: {e}")
        return None

def get_dashboard_data(token: str, skip: int = 0, limit: int = 50) -> Optional[Dict[str, Any]]:
    """Get all dashboard data in a single optimized call."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/violations/dashboard-data",
            params={"skip": skip, "limit": limit},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to get dashboard data: {e}")
        return None

# Legacy function names for backward compatibility
def submit_incident(token: str, description: str, store: str, location: str, offender: str, file: Optional[Any] = None) -> Optional[requests.Response]:
    """Legacy function - use submit_violation instead."""
    return submit_violation(token, description, store, location, location, offender, file=file)

def get_accessible_stores(token: str) -> List[Dict[str, Any]]:
    """Legacy function - use get_accessible_hoas instead."""
    return get_accessible_hoas(token)

def get_incidents_with_pagination(token: str, skip: int = 0, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Legacy function - use get_violations_with_pagination instead."""
    return get_violations_with_pagination(token, skip, limit)

def export_incidents_csv(token: str, filters: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
    """Legacy function - use export_violations_csv instead."""
    return export_violations_csv(token, filters)

