# tests/conftest.py
# Pytest configuration and fixtures for A.I.ncident tests

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app and database components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db, Base
from models import User, Store, Incident, Offender
from utils.auth_utils import get_password_hash, create_access_token

# Test database setup
@pytest.fixture(scope="session")
def test_db():
    """Create a file-based SQLite test database."""
    db_path = os.path.join(os.path.dirname(__file__), "test.db")
    # Remove any existing test DB file before starting
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield engine, TestingSessionLocal
    # Clean up test DB file after tests
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def db_session(test_db):
    """Create a database session for each test."""
    engine, TestingSessionLocal = test_db
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clear the database after each test
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# Test data fixtures
@pytest.fixture
def test_store(db_session):
    """Create a test store."""
    store = Store(
        name="Test Store",
        location="123 Test St, Test City, TC 12345"
    )
    db_session.add(store)
    db_session.commit()
    db_session.refresh(store)
    return store

@pytest.fixture
def test_user(db_session, test_store):
    """Create a test user."""
    user = User(
        username="testuser",
        hashed_password=get_password_hash("A!b2xQ7$"),
        email="test@example.com",
        role="employee",
        store_id=test_store.id,
        subscription_status="active",
        plan_id="pro",
        stripe_customer_id="cus_testuser"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        username="testadmin",
        hashed_password=get_password_hash("A!b2xQ7$"),
        email="admin@example.com",
        role="admin",
        subscription_status="active",
        plan_id="admin",
        stripe_customer_id="cus_testadmin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def test_staff(db_session, test_store):
    """Create a test staff user."""
    staff = User(
        username="teststaff",
        hashed_password=get_password_hash("A!b2xQ7$"),
        email="staff@example.com",
        role="staff",
        store_id=test_store.id,
        subscription_status="active",
        plan_id="pro",
        stripe_customer_id="cus_teststaff"
    )
    db_session.add(staff)
    db_session.commit()
    db_session.refresh(staff)
    return staff

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for a test user."""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(test_admin):
    """Create authentication headers for admin user."""
    token = create_access_token(data={"sub": test_admin.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def staff_headers(test_staff):
    """Create authentication headers for staff user."""
    token = create_access_token(data={"sub": test_staff.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_incident(db_session, test_user, test_store):
    """Create a test incident."""
    incident = Incident(
        description="Test incident description",
        summary="Test incident summary",
        tags="test,incident",
        severity="low",
        store_name=f"Store #{test_store.id:03d}",
        location="Test location",
        offender="Test offender",
        user_id=test_user.id
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident

# Utility functions for testing
def create_test_file(content: str = "test content", filename: str = "test.txt"):
    """Create a temporary test file."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
    temp_file.write(content.encode())
    temp_file.close()
    return temp_file.name

def cleanup_test_files():
    """Clean up any test files created during testing."""
    # This would be implemented based on your file storage strategy
    pass

@pytest.fixture(scope="session", autouse=True)
def set_global_db_override(test_db):
    """Globally override get_db to use the test DB for all tests and background tasks."""
    engine, TestingSessionLocal = test_db
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield 