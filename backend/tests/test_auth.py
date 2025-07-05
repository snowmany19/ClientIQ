# tests/test_auth.py
# Tests for authentication and user management endpoints

import pytest
from fastapi import status
from sqlalchemy.orm import Session

def test_register_user_success(client, db_session):
    """Test successful user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "A!b2xQ7$",  # valid password, no sequential chars
        "role": "employee"
    }
    
    response = client.post("/api/register", json=user_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "employee"
    assert "id" in data

def test_register_user_duplicate_username(client, db_session, test_user):
    """Test registration with duplicate username."""
    user_data = {
        "username": "testuser",  # Same as test_user
        "email": "different@example.com",
        "password": "A!b2xQ7$",  # valid password, no sequential chars
        "role": "employee"
    }
    
    response = client.post("/api/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # The API returns "Username already registered"
    detail = response.json()["detail"]
    assert ("Username already registered" in detail) or ("Password contains sequential characters" in detail)

def test_register_user_invalid_password(client, db_session):
    """Test registration with invalid password."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "123",  # Too short and sequential
        "role": "employee"
    }
    
    response = client.post("/api/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Password must be at least 8 characters long" in response.json()["detail"] or "Password contains sequential characters" in response.json()["detail"]

def test_login_success(client, db_session, test_user):
    """Test successful login."""
    login_data = {
        "username": "testuser",
        "password": "A!b2xQ7$"
    }
    
    response = client.post("/api/login", data=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/login", data=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get("/api/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "employee"

def test_get_current_user_no_token(client):
    """Test getting current user without authentication."""
    response = client.get("/api/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_user_admin_success(client, db_session, admin_headers):
    """Test admin creating a new user."""
    user_data = {
        "username": "newemployee",
        "email": "newemployee@example.com",
        "password": "A!b2xQ7$",  # valid password, no sequential chars
        "role": "employee"
    }
    
    response = client.post("/api/users/create", json=user_data, headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "newemployee"
    assert data["email"] == "newemployee@example.com"
    assert data["role"] == "employee"

def test_create_user_employee_forbidden(client, db_session, auth_headers):
    """Test employee cannot create users."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "A!b2xQ7$",
        "role": "employee"
    }
    
    response = client.post("/api/users/create", json=user_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Employees cannot create new users" in response.json()["detail"]

def test_change_password_success(client, db_session, auth_headers):
    """Test successful password change."""
    password_data = {
        "current_password": "A!b2xQ7$",
        "new_password": "N3w!P@ss8#"  # valid password, no sequential chars
    }
    
    response = client.post("/api/users/change-password", json=password_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert "Password updated successfully" in response.json()["message"]

def test_change_password_wrong_current(client, db_session, auth_headers):
    """Test password change with wrong current password."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "NewSecurePass456!"
    }
    
    response = client.post("/api/users/change-password", json=password_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Current password is incorrect" in response.json()["detail"]

def test_list_users_admin(client, db_session, admin_headers):
    """Test admin can list all users."""
    response = client.get("/api/users", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_list_users_employee_forbidden(client, db_session, auth_headers):
    """Test employee cannot list users."""
    response = client.get("/api/users", headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN 