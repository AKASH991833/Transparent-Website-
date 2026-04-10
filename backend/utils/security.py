from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from functools import wraps
from flask import session, redirect, url_for, flash

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def safe_filename(filename):
        """Sanitize filename"""
        return secure_filename(filename)
    
    @staticmethod
    def hash_password(password):
        """Hash password securely"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(stored_hash, password):
        """Verify password against hash"""
        return check_password_hash(stored_hash, password)
    
    @staticmethod
    def sanitize_input(text):
        """Basic input sanitization"""
        if not text:
            return text
        # Remove potential XSS patterns
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+="[^"]*"', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_price(price):
        """Validate price is positive number"""
        try:
            price = float(price)
            return price >= 0
        except (ValueError, TypeError):
            return False

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_protect(f):
    """Basic CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'csrf_token' not in session:
            import secrets
            session['csrf_token'] = secrets.token_hex(16)
        
        return f(*args, **kwargs)
    return decorated_function
