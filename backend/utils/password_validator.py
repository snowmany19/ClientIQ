# backend/utils/password_validator.py

import re
from typing import List, Tuple


class PasswordValidator:
    """Comprehensive password validation for production security."""
    
    def __init__(self, 
                 min_length: int = 8,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special: bool = True,
                 max_length: int = 128):
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password and return (is_valid, list_of_errors)."""
        errors = []
        
        # Check length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must be no more than {self.max_length} characters long")
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check for special characters
        if self.require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        if self._is_common_password(password):
            errors.append("Password is too common. Please choose a more unique password")
        
        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append("Password contains sequential characters (e.g., '123', 'abc')")
        
        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append("Password contains too many repeated characters")
        
        return len(errors) == 0, errors
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common password list."""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master', 'hello',
            'freedom', 'whatever', 'qazwsx', 'trustno1', 'jordan', 'harley',
            'ranger', 'iwantu', 'jennifer', 'hunter', 'buster', 'soccer',
            'baseball', 'tiger', 'charlie', 'andrew', 'michelle', 'love',
            'sunshine', 'jessica', 'asshole', '696969', 'amanda', 'access',
            'yankees', '987654321', 'dallas', 'austin', 'thunder', 'taylor',
            'matrix', 'mobilemail', 'mom', 'monitor', 'monitoring', 'montana',
            'moon', 'moscow'
        }
        return password.lower() in common_passwords
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters."""
        # Check for numeric sequences
        for i in range(len(password) - 2):
            if (password[i].isdigit() and password[i+1].isdigit() and password[i+2].isdigit()):
                if (int(password[i+1]) == int(password[i]) + 1 and 
                    int(password[i+2]) == int(password[i]) + 2):
                    return True
        
        # Check for alphabetic sequences
        for i in range(len(password) - 2):
            if (password[i].isalpha() and password[i+1].isalpha() and password[i+2].isalpha()):
                if (ord(password[i+1].lower()) == ord(password[i].lower()) + 1 and 
                    ord(password[i+2].lower()) == ord(password[i].lower()) + 2):
                    return True
        
        return False
    
    def _has_repeated_chars(self, password: str) -> bool:
        """Check for too many repeated characters."""
        if len(password) < 4:
            return False
        
        # Check for 4 or more consecutive identical characters
        for i in range(len(password) - 3):
            if password[i] == password[i+1] == password[i+2] == password[i+3]:
                return True
        
        return False
    
    def get_strength_score(self, password: str) -> int:
        """Get password strength score (0-100)."""
        score = 0
        
        # Length contribution
        score += min(len(password) * 4, 25)
        
        # Character variety contribution
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            score += 15
        
        # Deductions for weak patterns
        if self._is_common_password(password):
            score -= 30
        if self._has_sequential_chars(password):
            score -= 15
        if self._has_repeated_chars(password):
            score -= 10
        
        return max(0, min(100, score))
    
    def get_strength_label(self, score: int) -> str:
        """Get human-readable strength label."""
        if score >= 80:
            return "Very Strong"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak" 