# tests/test_incidents.py
# Tests for incident management endpoints

import pytest
from fastapi import status
from sqlalchemy.orm import Session

def test_create_incident_success(client, db_session, auth_headers, test_store):
    """Test successful incident creation."""
    incident_data = {
        "description": "Suspicious person loitering near entrance, wearing dark clothing and repeatedly checking their phone",
        "store": f"Store #{test_store.id:03d}",
        "location": "Main entrance",
        "offender": "Unknown male, dark clothing, approximately 6' tall"
    }
    
    response = client.post("/api/incidents/", data=incident_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == incident_data["description"]
    assert data["store_name"] == incident_data["store"]
    assert data["location"] == incident_data["location"]
    assert data["offender"] == incident_data["offender"]
    assert "id" in data

def test_create_incident_invalid_description(client, db_session, auth_headers, test_store):
    """Test incident creation with invalid description."""
    incident_data = {
        "description": "Too short",  # Less than 10 characters
        "store": f"Store #{test_store.id:03d}",
        "location": "Main entrance",
        "offender": "Unknown male"
    }
    
    response = client.post("/api/incidents/", data=incident_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Description must be at least 10 characters long" in response.json()["detail"]

def test_create_incident_wrong_store(client, db_session, auth_headers):
    """Test incident creation for store user doesn't have access to."""
    incident_data = {
        "description": "Suspicious person loitering near entrance, wearing dark clothing and repeatedly checking their phone",
        "store": "Store #999",  # Different store
        "location": "Main entrance",
        "offender": "Unknown male, dark clothing"
    }
    
    response = client.post("/api/incidents/", data=incident_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in response.json()["detail"]

def test_get_incidents_employee(client, db_session, auth_headers, test_incident):
    """Test employee can get incidents from their store."""
    response = client.get("/api/incidents/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Should only see incidents from their assigned store
    for incident in data:
        assert incident["store_name"] == test_incident.store_name

def test_get_incidents_admin(client, db_session, admin_headers, test_incident):
    """Test admin can get all incidents."""
    response = client.get("/api/incidents/", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Admin should see all incidents
    assert len(data) >= 1

def test_get_incident_by_id_success(client, db_session, auth_headers, test_incident):
    """Test getting specific incident by ID."""
    response = client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_incident.id
    assert data["description"] == test_incident.description

def test_get_incident_by_id_not_found(client, db_session, auth_headers):
    """Test getting non-existent incident."""
    response = client.get("/api/incidents/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_incident_by_id_wrong_store(client, db_session, auth_headers, test_incident):
    """Test getting incident from different store (should be filtered out)."""
    # Create incident in different store
    different_store_incident = Incident(
        description="Different store incident",
        store_name="Store #999",
        location="Different location",
        offender="Different offender",
        user_id=test_incident.user_id
    )
    db_session.add(different_store_incident)
    db_session.commit()
    
    response = client.get(f"/api/incidents/{different_store_incident.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in response.json()["detail"]

def test_delete_incident_admin_success(client, db_session, admin_headers, test_incident):
    """Test admin can delete any incident."""
    response = client.delete(f"/api/incidents/{test_incident.id}", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert "Incident deleted successfully" in response.json()["message"]

def test_delete_incident_staff_success(client, db_session, staff_headers, test_incident):
    """Test staff can delete incidents from their store."""
    response = client.delete(f"/api/incidents/{test_incident.id}", headers=staff_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert "Incident deleted successfully" in response.json()["message"]

def test_delete_incident_employee_forbidden(client, db_session, auth_headers, test_incident):
    """Test employee cannot delete incidents."""
    response = client.delete(f"/api/incidents/{test_incident.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Employees cannot delete incidents" in response.json()["detail"]

def test_delete_incident_not_found(client, db_session, admin_headers):
    """Test deleting non-existent incident."""
    response = client.delete("/api/incidents/99999", headers=admin_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_accessible_stores_employee(client, db_session, auth_headers, test_store):
    """Test employee can only see their assigned store."""
    response = client.get("/api/incidents/stores/accessible", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == test_store.id

def test_get_accessible_stores_admin(client, db_session, admin_headers, test_store):
    """Test admin can see all stores."""
    response = client.get("/api/incidents/stores/accessible", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_pagination_info(client, db_session, auth_headers, test_incident):
    """Test getting pagination information."""
    response = client.get("/api/incidents/pagination-info", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "pages" in data
    assert data["total"] >= 1

def test_incident_with_file_upload(client, db_session, auth_headers, test_store):
    """Test incident creation with file upload."""
    # Create a test image file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(b'fake image data')
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {
                "description": "Suspicious person loitering near entrance, wearing dark clothing and repeatedly checking their phone",
                "store": f"Store #{test_store.id:03d}",
                "location": "Main entrance",
                "offender": "Unknown male, dark clothing, approximately 6' tall"
            }
            
            response = client.post("/api/incidents/", data=data, files=files, headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["image_url"] is not None
    finally:
        os.unlink(tmp_file_path)

def test_incident_file_upload_invalid_type(client, db_session, auth_headers, test_store):
    """Test incident creation with invalid file type."""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(b'text file data')
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {
                "description": "Suspicious person loitering near entrance, wearing dark clothing and repeatedly checking their phone",
                "store": f"Store #{test_store.id:03d}",
                "location": "Main entrance",
                "offender": "Unknown male, dark clothing"
            }
            
            response = client.post("/api/incidents/", data=data, files=files, headers=auth_headers)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Only JPG and PNG files are allowed" in response.json()["detail"]
    finally:
        os.unlink(tmp_file_path) 