import requests
import os
from typing import Optional, Dict, Any

API_URL = "http://localhost:8000"

def handle_api_error(response: requests.Response, operation: str) -> str:
    """Handle API errors and return user-friendly messages."""
    try:
        error_data = response.json()
        detail = error_data.get('detail', 'Unknown error occurred')
        return f"{operation} failed: {detail}"
    except:
        if response.status_code == 401:
            return f"{operation} failed: Authentication required. Please log in again."
        elif response.status_code == 402:
            return f"{operation} failed: Payment required. Please subscribe to continue."
        elif response.status_code == 403:
            return f"{operation} failed: Access denied. You don't have permission for this action."
        elif response.status_code == 404:
            return f"{operation} failed: Resource not found."
        elif response.status_code == 422:
            return f"{operation} failed: Invalid data provided. Please check your input."
        elif response.status_code >= 500:
            return f"{operation} failed: Server error. Please try again later."
        else:
            return f"{operation} failed: HTTP {response.status_code}"

def get_jwt_token(username: str, password: str) -> Optional[str]:
    """Get JWT token with error handling."""
    if not username or not password:
        print("⚠️ Username and password are required.")
        return None
    
    try:
        res = requests.post(f"{API_URL}/api/login", data={
            "username": username,
            "password": password
        }, timeout=10)
        
        if res.status_code == 200:
            token = res.json().get("access_token")
            if token:
                return token
            else:
                print("⚠️ No token received from server.")
                return None
        else:
            error_msg = handle_api_error(res, "Login")
            print(f"❌ {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Login failed: Request timed out. Please check your connection.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Login failed: Cannot connect to server. Please check if the backend is running.")
        return None
    except Exception as e:
        print(f"❌ Login failed: Unexpected error - {str(e)}")
        return None

def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """Get user info with error handling."""
    if not token:
        print("⚠️ No token available. Please log in.")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/api/me", headers=headers, timeout=10)
        
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch user info")
            print(f"❌ {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ User info fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ User info fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        print(f"❌ User info fetch failed: Unexpected error - {str(e)}")
        return None

def submit_incident(description, store, location, offender, file=None, token=None) -> Optional[requests.Response]:
    """Submit incident with comprehensive error handling."""
    if not description or not store or not location:
        print("❌ Missing required fields: description, store, and location are required.")
        return None
    
    url = f"{API_URL}/api/incidents/"

    data = {
        "description": description,
        "store": store,
        "location": location,
        "offender": offender or ""
    }

    files = {"file": (file.name, file, file.type)} if file is not None else None

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
        return response
    except requests.exceptions.Timeout:
        print("❌ Incident submission failed: Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Incident submission failed: Cannot connect to server.")
        return None
    except Exception as e:
        print(f"❌ Incident submission failed: Unexpected error - {str(e)}")
        return None

def get_accessible_stores(token: str) -> Optional[list]:
    """Get stores that the current user can access based on their role."""
    if not token:
        print("⚠️ No token available. Please log in.")
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/api/incidents/stores/accessible", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch accessible stores")
            print(f"❌ {error_msg}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Store fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Store fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        print(f"❌ Store fetch failed: Unexpected error - {str(e)}")
        return None

def get_incidents_with_pagination(token: str, skip: int = 0, limit: int = 50) -> Optional[list]:
    """Get incidents with pagination."""
    if not token:
        print("⚠️ No token available. Please log in.")
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/api/incidents/?skip={skip}&limit={limit}", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 402:
            # Payment required - let the calling function handle the redirect
            return None
        else:
            error_msg = handle_api_error(res, "Fetch incidents")
            print(f"❌ {error_msg}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Incidents fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Incidents fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        print(f"❌ Incidents fetch failed: Unexpected error - {str(e)}")
        return None

def get_pagination_info(token: str) -> Optional[dict]:
    """Get pagination information for incidents."""
    if not token:
        print("⚠️ No token available. Please log in.")
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/api/incidents/pagination-info", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            error_msg = handle_api_error(res, "Fetch pagination info")
            print(f"❌ {error_msg}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Pagination info fetch failed: Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Pagination info fetch failed: Cannot connect to server.")
        return None
    except Exception as e:
        print(f"❌ Pagination info fetch failed: Unexpected error - {str(e)}")
        return None

