# tests/test_validation.py
# Tests for input validation utilities

import pytest
from utils.validation import InputValidator, ValidationException

class TestInputValidator:
    """Test cases for InputValidator class."""
    
    def test_validate_incident_description_valid(self):
        """Test valid incident description."""
        description = "This is a valid incident description with sufficient detail about what happened."
        result = InputValidator.validate_incident_description(description)
        assert result == description
    
    def test_validate_incident_description_too_short(self):
        """Test incident description that's too short."""
        description = "Too short"
        with pytest.raises(ValidationException, match="Description must be at least 10 characters long"):
            InputValidator.validate_incident_description(description)
    
    def test_validate_incident_description_too_long(self):
        """Test incident description that's too long."""
        description = "x" * 2001  # More than 2000 characters
        with pytest.raises(ValidationException, match="Description must be less than 2000 characters"):
            InputValidator.validate_incident_description(description)
    
    def test_validate_incident_description_empty(self):
        """Test empty incident description."""
        with pytest.raises(ValidationException, match="Description is required"):
            InputValidator.validate_incident_description("")
    
    def test_validate_store_name_valid(self):
        """Test valid store name format."""
        store_name = "Store #001"
        result = InputValidator.validate_store_name(store_name)
        assert result == store_name
    
    def test_validate_store_name_invalid_format(self):
        """Test invalid store name format."""
        store_name = "Store 1"  # Missing #
        with pytest.raises(ValidationException, match="Store name must be in format 'Store #XXX'"):
            InputValidator.validate_store_name(store_name)
    
    def test_validate_store_name_empty(self):
        """Test empty store name."""
        with pytest.raises(ValidationException, match="Store name is required"):
            InputValidator.validate_store_name("")
    
    def test_validate_location_valid(self):
        """Test valid location."""
        location = "Main entrance"
        result = InputValidator.validate_location(location)
        assert result == location
    
    def test_validate_location_too_short(self):
        """Test location that's too short."""
        location = "A"  # Less than 2 characters
        with pytest.raises(ValidationException, match="Location must be at least 2 characters long"):
            InputValidator.validate_location(location)
    
    def test_validate_location_too_long(self):
        """Test location that's too long."""
        location = "x" * 101  # More than 100 characters
        with pytest.raises(ValidationException, match="Location must be less than 100 characters"):
            InputValidator.validate_location(location)
    
    def test_validate_offender_valid(self):
        """Test valid offender description."""
        offender = "Unknown male, dark clothing"
        result = InputValidator.validate_offender(offender)
        assert result == offender
    
    def test_validate_offender_too_short(self):
        """Test offender description that's too short."""
        offender = "A"  # Less than 2 characters
        with pytest.raises(ValidationException, match="Offender information must be at least 2 characters long"):
            InputValidator.validate_offender(offender)
    
    def test_validate_username_valid(self):
        """Test valid username."""
        username = "john_doe123"
        result = InputValidator.validate_username(username)
        assert result == username
    
    def test_validate_username_too_short(self):
        """Test username that's too short."""
        username = "ab"  # Less than 3 characters
        with pytest.raises(ValidationException, match="Username must be 3-20 characters long"):
            InputValidator.validate_username(username)
    
    def test_validate_username_too_long(self):
        """Test username that's too long."""
        username = "a" * 21  # More than 20 characters
        with pytest.raises(ValidationException, match="Username must be 3-20 characters long"):
            InputValidator.validate_username(username)
    
    def test_validate_username_invalid_characters(self):
        """Test username with invalid characters."""
        username = "john-doe"  # Contains hyphen
        with pytest.raises(ValidationException, match="Username must be 3-20 characters long and contain only letters, numbers, and underscores"):
            InputValidator.validate_username(username)
    
    def test_validate_email_valid(self):
        """Test valid email."""
        email = "john.doe@example.com"
        result = InputValidator.validate_email(email)
        assert result == email
    
    def test_validate_email_invalid_format(self):
        """Test invalid email format."""
        email = "invalid-email"
        with pytest.raises(ValidationException, match="Invalid email format"):
            InputValidator.validate_email(email)
    
    def test_validate_password_valid(self):
        """Test valid password."""
        password = "SecurePass123!"
        result = InputValidator.validate_password(password)
        assert result == password
    
    def test_validate_password_too_short(self):
        """Test password that's too short."""
        password = "123"
        with pytest.raises(ValidationException, match="Password must be at least 8 characters long"):
            InputValidator.validate_password(password)
    
    def test_validate_password_too_long(self):
        """Test password that's too long."""
        password = "x" * 129  # More than 128 characters
        with pytest.raises(ValidationException, match="Password must be less than 128 characters"):
            InputValidator.validate_password(password)
    
    def test_validate_password_weak(self):
        """Test weak password."""
        password = "password"  # Common weak password
        with pytest.raises(ValidationException, match="Password is too common"):
            InputValidator.validate_password(password)
    
    def test_validate_pagination_params_valid(self):
        """Test valid pagination parameters."""
        skip, limit = InputValidator.validate_pagination_params(0, 50)
        assert skip == 0
        assert limit == 50
    
    def test_validate_pagination_params_invalid_skip(self):
        """Test invalid skip parameter."""
        with pytest.raises(ValidationException, match="Skip must be 0 or greater"):
            InputValidator.validate_pagination_params(-1, 50)
    
    def test_validate_pagination_params_invalid_limit(self):
        """Test invalid limit parameter."""
        with pytest.raises(ValidationException, match="Limit must be between 1 and 100"):
            InputValidator.validate_pagination_params(0, 0)
        
        with pytest.raises(ValidationException, match="Limit must be between 1 and 100"):
            InputValidator.validate_pagination_params(0, 101)
    
    def test_sanitize_filename_valid(self):
        """Test filename sanitization."""
        filename = "test_image.jpg"
        result = InputValidator.sanitize_filename(filename)
        assert result == "test_image.jpg"
    
    def test_sanitize_filename_with_path_traversal(self):
        """Test filename with path traversal attempt."""
        filename = "../../../etc/passwd"
        result = InputValidator.sanitize_filename(filename)
        assert result == "passwd"  # Should remove path traversal
    
    def test_sanitize_filename_with_special_chars(self):
        """Test filename with special characters."""
        filename = "test@file#.jpg"
        result = InputValidator.sanitize_filename(filename)
        assert result == "testfile.jpg"  # Should remove special chars
    
    def test_validate_file_path_valid(self):
        """Test valid file path."""
        file_path = "incident_123.pdf"
        result = InputValidator.validate_file_path(file_path, [".pdf"])
        assert result == file_path
    
    def test_validate_file_path_path_traversal(self):
        """Test file path with path traversal."""
        file_path = "../../../etc/passwd"
        with pytest.raises(ValidationException, match="Invalid file path"):
            InputValidator.validate_file_path(file_path)
    
    def test_validate_file_path_wrong_extension(self):
        """Test file path with wrong extension."""
        file_path = "incident_123.txt"
        with pytest.raises(ValidationException, match="File must have one of these extensions"):
            InputValidator.validate_file_path(file_path, [".pdf", ".jpg"])

def test_validate_incident_data_integration():
    """Test the validate_incident_data function with valid data."""
    from utils.validation import validate_incident_data
    
    # Mock file object
    class MockFile:
        def __init__(self):
            self.size = 1024
            self.content_type = "image/jpeg"
            self.filename = "test.jpg"
    
    mock_file = MockFile()
    
    result = validate_incident_data(
        description="Valid incident description with sufficient detail",
        store="Store #001",
        location="Main entrance",
        offender="Unknown male, dark clothing",
        file=mock_file
    )
    
    assert result["description"] == "Valid incident description with sufficient detail"
    assert result["store"] == "Store #001"
    assert result["location"] == "Main entrance"
    assert result["offender"] == "Unknown male, dark clothing"
    assert result["filename"] == "test.jpg"

def test_validate_user_data_integration():
    """Test the validate_user_data function with valid data."""
    from utils.validation import validate_user_data
    
    result = validate_user_data(
        username="john_doe",
        email="john.doe@example.com",
        password="SecurePass123!"
    )
    
    assert result["username"] == "john_doe"
    assert result["email"] == "john.doe@example.com"
    assert result["password"] == "SecurePass123!" 