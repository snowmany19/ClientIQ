# utils/api.py

import requests
import requests
import json

API_URL = "http://127.0.0.1:8000"

def get_jwt_token(username: str, password: str):
    try:
        res = requests.post(f"{API_URL}/auth/login", data={
            "username": username,
            "password": password
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        else:
            print("⚠️ Login failed:", res.text)
            return None
    except Exception as e:
        print("❌ Error getting JWT token:", e)
        return None

def get_user_info(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/auth/me", headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            print("⚠️ Failed to fetch user info:", res.text)
            return None
    except Exception as e:
        print("❌ Error fetching user info:", e)
        return None


def submit_incident(description, store, location, offender, file=None, token=None):
    url = "http://127.0.0.1:8000/incidents/"
    
    data = {
        "description": description,
        "store": store,
        "location": location,
        "offender": offender
    }

    files = {"file": (file.name, file, file.type)} if file is not None else None

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(url, data=data, files=files, headers=headers)
        return response
    except Exception as e:
        print(f"❌ API submission error: {e}")
        return None
