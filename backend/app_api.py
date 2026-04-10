"""
ANSH AIR COOL - Production-Ready Secure Backend API
Senior Developer Implementation with Maximum Security
"""

import os
import re
import json
import secrets
import bleach
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import jwt
import logging

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', secrets.token_hex(64))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 2
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
RATE_LIMIT_SECONDS = 60
MAX_REQUESTS_PER_MINUTE = 30

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SECURITY UTILITIES
# ═══════════════════════════════════════════════════════════

# Rate limiting storage (use Redis in production)
rate_limit_store = {}

def check_rate_limit(client_ip):
    """Rate limiting per IP"""
    now = datetime.now(timezone.utc)
    if client_ip in rate_limit_store:
        requests, last_request = rate_limit_store[client_ip]
        if (now - last_request).seconds < RATE_LIMIT_SECONDS and requests >= MAX_REQUESTS_PER_MINUTE:
            return False
        if (now - last_request).seconds >= RATE_LIMIT_SECONDS:
            rate_limit_store[client_ip] = (1, now)
        else:
            rate_limit_store[client_ip] = (requests + 1, last_request)
    else:
        rate_limit_store[client_ip] = (1, now)
    return True

def sanitize_input(text):
    """XSS Protection - Sanitize user input"""
    if not text:
        return ""
    return bleach.clean(str(text), tags=[], attributes={}, strip=True)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url):
    """Validate URL format (for image URLs)"""
    if not url:
        return False
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_token(user_id, username):
    """Generate JWT token with expiration"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ═══════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════════════════════

def get_db():
    """Get database connection with error handling"""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DB', 'ac_service_billing'),
                dictionary=True,
                autocommit=True
            )
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    return g.db

@app.teardown_appcontext
def close_db(e):
    """Close database connection"""
    db = g.pop('db', None)
    if db:
        db.close()

# ═══════════════════════════════════════════════════════════
# AUTHENTICATION DECORATOR
# ═══════════════════════════════════════════════════════════

def token_required(f):
    """JWT token-based authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Rate limiting
        client_ip = request.remote_addr
        if not check_rate_limit(client_ip):
            return jsonify({'error': 'Too many requests. Please try again later.'}), 429

        # Get token from header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Verify user exists
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, username, is_active FROM admin_users WHERE id = %s', (payload['user_id'],))
        user = cursor.fetchone()
        cursor.close()

        if not user or not user['is_active']:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════════════════

def init_db():
    """Initialize database with all required tables"""
    try:
        # Create database
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{os.getenv('MYSQL_DB', 'ac_service_billing')}`")
        cursor.close()
        conn.close()

        # Connect to database directly (no Flask g object)
        db = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'ac_service_billing')
        )
        cursor = db.cursor(dictionary=True)

        # Drop existing tables to recreate with new schema
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
        cursor.execute('DROP TABLE IF EXISTS marquee_items')
        cursor.execute('DROP TABLE IF EXISTS hero_settings')
        cursor.execute('DROP TABLE IF EXISTS contact_submissions')
        cursor.execute('DROP TABLE IF EXISTS site_settings')
        cursor.execute('DROP TABLE IF EXISTS admin_users')
        cursor.execute('DROP TABLE IF EXISTS services')
        cursor.execute('DROP TABLE IF EXISTS products')
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        db.commit()

        # Products table
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(80) NOT NULL,
            buy_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            rent_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            old_price DECIMAL(10,2),
            description_buy TEXT,
            description_rent TEXT,
            image VARCHAR(500),
            rating DECIMAL(2,1) DEFAULT 4.5,
            rating_count INT DEFAULT 0,
            badge VARCHAR(50),
            features JSON,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_category (category),
            INDEX idx_active (is_active),
            INDEX idx_order (order_index)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Services table
        cursor.execute('''CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            description TEXT,
            image VARCHAR(500),
            icon VARCHAR(80),
            features JSON,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_active (is_active),
            INDEX idx_order (order_index)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Admin users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS admin_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(120),
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Contact submissions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS contact_submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            email VARCHAR(120) NOT NULL,
            phone VARCHAR(30),
            message TEXT,
            is_read BOOLEAN DEFAULT FALSE,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_read (is_read),
            INDEX idx_submitted (submitted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Site settings table
        cursor.execute('''CREATE TABLE IF NOT EXISTS site_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            site_name VARCHAR(150) DEFAULT 'ANSH AIR COOL',
            phone VARCHAR(30),
            whatsapp VARCHAR(30),
            email VARCHAR(120),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Hero settings table
        cursor.execute('''CREATE TABLE IF NOT EXISTS hero_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            trust_badge_text VARCHAR(200) DEFAULT 'Indias #1 Trusted AC Brand',
            title_line_1 VARCHAR(100) DEFAULT 'Experience',
            title_line_2 VARCHAR(100) DEFAULT 'Ultimate Cooling',
            title_line_3 VARCHAR(100) DEFAULT 'Like Never Before',
            subtitle VARCHAR(500) DEFAULT 'Advanced inverter technology that saves up to 60 percent electricity',
            stat_1_number INT DEFAULT 15,
            stat_1_suffix VARCHAR(10) DEFAULT '+',
            stat_1_label VARCHAR(100) DEFAULT 'Years Experience',
            stat_2_number INT DEFAULT 50,
            stat_2_suffix VARCHAR(10) DEFAULT 'K+',
            stat_2_label VARCHAR(100) DEFAULT 'Happy Customers',
            stat_3_number INT DEFAULT 99,
            stat_3_suffix VARCHAR(10) DEFAULT '%',
            stat_3_label VARCHAR(100) DEFAULT 'Satisfaction Rate',
            quick_feature_1 VARCHAR(100) DEFAULT '5 Star Rating',
            quick_feature_2 VARCHAR(100) DEFAULT 'Free Delivery',
            quick_feature_3 VARCHAR(100) DEFAULT '10 Year Warranty',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Marquee items table
        cursor.execute('''CREATE TABLE IF NOT EXISTS marquee_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            main_text VARCHAR(100) NOT NULL,
            sub_text VARCHAR(200) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            order_index INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_active (is_active),
            INDEX idx_order (order_index)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Seed default admin user
        cursor.execute('SELECT COUNT(*) as cnt FROM admin_users')
        result = cursor.fetchone()
        if result['cnt'] == 0:
            cursor.execute(
                'INSERT INTO admin_users (username, password, email) VALUES (%s, %s, %s)',
                ('admin', generate_password_hash('admin123'), 'admin@anshaircool.com')
            )

        # Seed default site settings
        cursor.execute('SELECT COUNT(*) as cnt FROM site_settings')
        result = cursor.fetchone()
        if result['cnt'] == 0:
            cursor.execute('''INSERT INTO site_settings 
                (site_name, phone, whatsapp, email, address) 
                VALUES (%s, %s, %s, %s, %s)''',
                ('ANSH AIR COOL', '+919876543210', '919876543210', 
                 'support@anshaircool.com', 'Mumbai, India'))

        # Seed default hero settings
        cursor.execute('SELECT COUNT(*) as cnt FROM hero_settings')
        result = cursor.fetchone()
        if result['cnt'] == 0:
            cursor.execute('''INSERT INTO hero_settings 
                (trust_badge_text, title_line_1, title_line_2, title_line_3, subtitle,
                 stat_1_number, stat_1_suffix, stat_1_label,
                 stat_2_number, stat_2_suffix, stat_2_label,
                 stat_3_number, stat_3_suffix, stat_3_label,
                 quick_feature_1, quick_feature_2, quick_feature_3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                ('Indias #1 Trusted AC Brand', 'Experience', 'Ultimate Cooling', 'Like Never Before',
                 'Advanced inverter technology that saves up to 60 percent electricity',
                 15, '+', 'Years Experience',
                 50, 'K+', 'Happy Customers',
                 99, '%', 'Satisfaction Rate',
                 '5 Star Rating', 'Free Delivery', '10 Year Warranty'))

        # Seed default marquee items
        cursor.execute('SELECT COUNT(*) as cnt FROM marquee_items')
        result = cursor.fetchone()
        if result['cnt'] == 0:
            marquee_data = [
                ('ANSH AIR COOL', 'Premium AC Services', 1),
                ('ANSH AIR COOL', 'Installation & Repair', 2),
                ('ANSH AIR COOL', 'Best Cooling Solutions', 3),
                ('ANSH AIR COOL', 'Trusted by 50K+ Customers', 4)
            ]
            for main_text, sub_text, order_idx in marquee_data:
                cursor.execute(
                    'INSERT INTO marquee_items (main_text, sub_text, order_index) VALUES (%s, %s, %s)',
                    (main_text, sub_text, order_idx)
                )

        cursor.close()
        logger.info("✅ Database initialized successfully!")

    except Error as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise

# ═══════════════════════════════════════════════════════════
# PUBLIC API ENDPOINTS (No Auth Required)
# ═══════════════════════════════════════════════════════════

@app.route('/api/public/site-settings', methods=['GET'])
def get_site_settings():
    """Get public site settings"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM site_settings LIMIT 1')
        settings = cursor.fetchone()
        cursor.close()
        return jsonify(settings or {})
    except Error as e:
        logger.error(f"Error fetching site settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/public/hero-data', methods=['GET'])
def get_hero_data():
    """Get hero section data"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM hero_settings LIMIT 1')
        hero_data = cursor.fetchone()
        cursor.close()
        return jsonify(hero_data or {})
    except Error as e:
        logger.error(f"Error fetching hero data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/public/marquee', methods=['GET'])
def get_marquee():
    """Get active marquee items"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM marquee_items WHERE is_active=TRUE ORDER BY order_index')
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    except Error as e:
        logger.error(f"Error fetching marquee: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/public/products', methods=['GET'])
def get_public_products():
    """Get active products for public display"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM products WHERE is_active=TRUE ORDER BY order_index, id')
        products = cursor.fetchall()
        cursor.close()
        
        # Convert features JSON string to list
        for product in products:
            if product.get('features') and isinstance(product['features'], str):
                product['features'] = json.loads(product['features'])
        
        return jsonify(products)
    except Error as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/public/services', methods=['GET'])
def get_public_services():
    """Get active services for public display"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM services WHERE is_active=TRUE ORDER BY order_index')
        services = cursor.fetchall()
        cursor.close()
        
        # Convert features JSON string to list
        for service in services:
            if service.get('features') and isinstance(service['features'], str):
                service['features'] = json.loads(service['features'])
        
        return jsonify(services)
    except Error as e:
        logger.error(f"Error fetching services: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ═══════════════════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Secure admin login with JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        username = sanitize_input(data.get('username', ''))
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Rate limiting
        client_ip = request.remote_addr
        if not check_rate_limit(client_ip):
            return jsonify({'error': 'Too many attempts. Please try again later.'}), 429

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, username, password, is_active, email FROM admin_users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user or not check_password_hash(user['password'], password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user['is_active']:
            return jsonify({'error': 'Account is disabled'}), 403

        # Generate JWT token
        token = generate_token(user['id'], user['username'])

        # Update last login
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE admin_users SET last_login = NOW() WHERE id = %s', (user['id'],))
        cursor.close()

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        })

    except Error as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ═══════════════════════════════════════════════════════════
# ADMIN API ENDPOINTS (Auth Required)
# ═══════════════════════════════════════════════════════════

# ---- DASHBOARD ----

@app.route('/api/admin/dashboard', methods=['GET'])
@token_required
def admin_dashboard():
    """Get dashboard statistics"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute('SELECT COUNT(*) as count FROM products WHERE is_active=TRUE')
        active_products = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM services WHERE is_active=TRUE')
        active_services = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contact_submissions')
        total_contacts = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM contact_submissions WHERE is_read=FALSE')
        unread_contacts = cursor.fetchone()['count']
        
        cursor.close()
        
        return jsonify({
            'active_products': active_products,
            'active_services': active_services,
            'total_contacts': total_contacts,
            'unread_contacts': unread_contacts
        })
        
    except Error as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- HERO SETTINGS ----

@app.route('/api/admin/hero', methods=['GET'])
@token_required
def get_hero_settings():
    """Get hero settings for admin editing"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM hero_settings LIMIT 1')
        settings = cursor.fetchone()
        cursor.close()
        return jsonify(settings or {})
    except Error as e:
        logger.error(f"Error fetching hero settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/hero', methods=['PUT'])
@token_required
def update_hero_settings():
    """Update hero settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''UPDATE hero_settings SET
            trust_badge_text = %s,
            title_line_1 = %s,
            title_line_2 = %s,
            title_line_3 = %s,
            subtitle = %s,
            stat_1_number = %s,
            stat_1_suffix = %s,
            stat_1_label = %s,
            stat_2_number = %s,
            stat_2_suffix = %s,
            stat_2_label = %s,
            stat_3_number = %s,
            stat_3_suffix = %s,
            stat_3_label = %s,
            quick_feature_1 = %s,
            quick_feature_2 = %s,
            quick_feature_3 = %s
            WHERE id = 1''',
            (
                sanitize_input(data.get('trust_badge_text', '')),
                sanitize_input(data.get('title_line_1', '')),
                sanitize_input(data.get('title_line_2', '')),
                sanitize_input(data.get('title_line_3', '')),
                sanitize_input(data.get('subtitle', '')),
                int(data.get('stat_1_number', 15)),
                sanitize_input(data.get('stat_1_suffix', '+')),
                sanitize_input(data.get('stat_1_label', '')),
                int(data.get('stat_2_number', 50)),
                sanitize_input(data.get('stat_2_suffix', 'K+')),
                sanitize_input(data.get('stat_2_label', '')),
                int(data.get('stat_3_number', 99)),
                sanitize_input(data.get('stat_3_suffix', '%')),
                sanitize_input(data.get('stat_3_label', '')),
                sanitize_input(data.get('quick_feature_1', '')),
                sanitize_input(data.get('quick_feature_2', '')),
                sanitize_input(data.get('quick_feature_3', ''))
            ))
        
        cursor.close()
        logger.info(f"Hero settings updated by {request.current_user['username']}")
        return jsonify({'message': 'Hero settings updated successfully'})
        
    except Error as e:
        logger.error(f"Error updating hero settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- SITE SETTINGS ----

@app.route('/api/admin/site-settings', methods=['GET'])
@token_required
def get_site_settings_admin():
    """Get site settings for admin"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM site_settings LIMIT 1')
        settings = cursor.fetchone()
        cursor.close()
        return jsonify(settings or {})
    except Error as e:
        logger.error(f"Error fetching site settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/site-settings', methods=['PUT'])
@token_required
def update_site_settings():
    """Update site settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''UPDATE site_settings SET
            site_name = %s,
            phone = %s,
            whatsapp = %s,
            email = %s,
            address = %s
            WHERE id = 1''',
            (
                sanitize_input(data.get('site_name', '')),
                sanitize_input(data.get('phone', '')),
                sanitize_input(data.get('whatsapp', '')),
                sanitize_input(data.get('email', '')),
                sanitize_input(data.get('address', ''))
            ))
        
        cursor.close()
        logger.info(f"Site settings updated by {request.current_user['username']}")
        return jsonify({'message': 'Site settings updated successfully'})
        
    except Error as e:
        logger.error(f"Error updating site settings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- MARQUEE MANAGEMENT ----

@app.route('/api/admin/marquee', methods=['GET'])
@token_required
def get_marquee_admin():
    """Get all marquee items for admin"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM marquee_items ORDER BY order_index')
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    except Error as e:
        logger.error(f"Error fetching marquee items: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/marquee', methods=['POST'])
@token_required
def create_marquee_item():
    """Create new marquee item"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        main_text = sanitize_input(data.get('main_text', ''))
        sub_text = sanitize_input(data.get('sub_text', ''))
        order_index = int(data.get('order_index', 0))

        if not main_text or not sub_text:
            return jsonify({'error': 'Main text and sub text are required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO marquee_items (main_text, sub_text, order_index, is_active) 
                         VALUES (%s, %s, %s, TRUE)''',
                      (main_text, sub_text, order_index))
        cursor.close()
        
        logger.info(f"Marquee item created by {request.current_user['username']}")
        return jsonify({'message': 'Marquee item created successfully'}), 201
        
    except Error as e:
        logger.error(f"Error creating marquee item: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/marquee/<int:id>', methods=['PUT'])
@token_required
def update_marquee_item(id):
    """Update marquee item"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE marquee_items SET
                         main_text = %s,
                         sub_text = %s,
                         order_index = %s,
                         is_active = %s
                         WHERE id = %s''',
                      (
                          sanitize_input(data.get('main_text', '')),
                          sanitize_input(data.get('sub_text', '')),
                          int(data.get('order_index', 0)),
                          data.get('is_active', True),
                          id
                      ))
        cursor.close()
        
        logger.info(f"Marquee item {id} updated by {request.current_user['username']}")
        return jsonify({'message': 'Marquee item updated successfully'})
        
    except Error as e:
        logger.error(f"Error updating marquee item: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/marquee/<int:id>', methods=['DELETE'])
@token_required
def delete_marquee_item(id):
    """Delete marquee item"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM marquee_items WHERE id = %s', (id,))
        cursor.close()
        
        logger.info(f"Marquee item {id} deleted by {request.current_user['username']}")
        return jsonify({'message': 'Marquee item deleted successfully'})
        
    except Error as e:
        logger.error(f"Error deleting marquee item: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- PRODUCTS MANAGEMENT ----

@app.route('/api/admin/products', methods=['GET'])
@token_required
def get_products():
    """Get all products"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM products ORDER BY order_index, id DESC')
        products = cursor.fetchall()
        
        # Parse JSON features
        for product in products:
            if product.get('features') and isinstance(product['features'], str):
                product['features'] = json.loads(product['features'])
        
        cursor.close()
        return jsonify(products)
    except Error as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/products', methods=['POST'])
@token_required
def create_product():
    """Create new product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        # Validate required fields
        required = ['name', 'category', 'buy_price', 'rent_price']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate image URL if provided
        image = data.get('image', '')
        if image and not validate_url(image) and not image.startswith('/static/'):
            return jsonify({'error': 'Invalid image URL format'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO products 
                         (name, category, buy_price, rent_price, old_price, 
                          description_buy, description_rent, image, rating, rating_count,
                          badge, features, is_active, order_index) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                      (
                          sanitize_input(data['name']),
                          sanitize_input(data['category']),
                          float(data['buy_price']),
                          float(data['rent_price']),
                          float(data.get('old_price', 0)),
                          sanitize_input(data.get('description_buy', '')),
                          sanitize_input(data.get('description_rent', '')),
                          image,
                          float(data.get('rating', 4.5)),
                          int(data.get('rating_count', 0)),
                          sanitize_input(data.get('badge', '')),
                          json.dumps(data.get('features', [])),
                          data.get('is_active', True),
                          int(data.get('order_index', 0))
                      ))
        cursor.close()
        
        logger.info(f"Product created by {request.current_user['username']}")
        return jsonify({'message': 'Product created successfully'}), 201
        
    except Error as e:
        logger.error(f"Error creating product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/products/<int:id>', methods=['PUT'])
@token_required
def update_product(id):
    """Update product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        # Validate image URL if provided
        image = data.get('image')
        if image and not validate_url(image) and not image.startswith('/static/'):
            return jsonify({'error': 'Invalid image URL format'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE products SET
                         name = %s,
                         category = %s,
                         buy_price = %s,
                         rent_price = %s,
                         old_price = %s,
                         description_buy = %s,
                         description_rent = %s,
                         image = %s,
                         rating = %s,
                         rating_count = %s,
                         badge = %s,
                         features = %s,
                         is_active = %s,
                         order_index = %s
                         WHERE id = %s''',
                      (
                          sanitize_input(data.get('name', '')),
                          sanitize_input(data.get('category', '')),
                          float(data.get('buy_price', 0)),
                          float(data.get('rent_price', 0)),
                          float(data.get('old_price', 0)),
                          sanitize_input(data.get('description_buy', '')),
                          sanitize_input(data.get('description_rent', '')),
                          image,
                          float(data.get('rating', 4.5)),
                          int(data.get('rating_count', 0)),
                          sanitize_input(data.get('badge', '')),
                          json.dumps(data.get('features', [])),
                          data.get('is_active', True),
                          int(data.get('order_index', 0)),
                          id
                      ))
        cursor.close()
        
        logger.info(f"Product {id} updated by {request.current_user['username']}")
        return jsonify({'message': 'Product updated successfully'})
        
    except Error as e:
        logger.error(f"Error updating product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/products/<int:id>', methods=['DELETE'])
@token_required
def delete_product(id):
    """Delete product"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM products WHERE id = %s', (id,))
        cursor.close()
        
        logger.info(f"Product {id} deleted by {request.current_user['username']}")
        return jsonify({'message': 'Product deleted successfully'})
        
    except Error as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- SERVICES MANAGEMENT ----

@app.route('/api/admin/services', methods=['GET'])
@token_required
def get_services():
    """Get all services"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM services ORDER BY order_index')
        services = cursor.fetchall()
        
        # Parse JSON features
        for service in services:
            if service.get('features') and isinstance(service['features'], str):
                service['features'] = json.loads(service['features'])
        
        cursor.close()
        return jsonify(services)
    except Error as e:
        logger.error(f"Error fetching services: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/services', methods=['POST'])
@token_required
def create_service():
    """Create new service"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        # Validate image URL
        image = data.get('image', '')
        if image and not validate_url(image) and not image.startswith('/static/'):
            return jsonify({'error': 'Invalid image URL format'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO services 
                         (title, description, image, icon, features, is_active, order_index) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                      (
                          sanitize_input(data['title']),
                          sanitize_input(data.get('description', '')),
                          image,
                          sanitize_input(data.get('icon', '')),
                          json.dumps(data.get('features', [])),
                          data.get('is_active', True),
                          int(data.get('order_index', 0))
                      ))
        cursor.close()
        
        logger.info(f"Service created by {request.current_user['username']}")
        return jsonify({'message': 'Service created successfully'}), 201
        
    except Error as e:
        logger.error(f"Error creating service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/services/<int:id>', methods=['PUT'])
@token_required
def update_service(id):
    """Update service"""
    try:
        data = request.get_json()
        
        # Validate image URL
        image = data.get('image')
        if image and not validate_url(image) and not image.startswith('/static/'):
            return jsonify({'error': 'Invalid image URL format'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE services SET
                         title = %s,
                         description = %s,
                         image = %s,
                         icon = %s,
                         features = %s,
                         is_active = %s,
                         order_index = %s
                         WHERE id = %s''',
                      (
                          sanitize_input(data.get('title', '')),
                          sanitize_input(data.get('description', '')),
                          image,
                          sanitize_input(data.get('icon', '')),
                          json.dumps(data.get('features', [])),
                          data.get('is_active', True),
                          int(data.get('order_index', 0)),
                          id
                      ))
        cursor.close()
        
        logger.info(f"Service {id} updated by {request.current_user['username']}")
        return jsonify({'message': 'Service updated successfully'})
        
    except Error as e:
        logger.error(f"Error updating service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/services/<int:id>', methods=['DELETE'])
@token_required
def delete_service(id):
    """Delete service"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM services WHERE id = %s', (id,))
        cursor.close()
        
        logger.info(f"Service {id} deleted by {request.current_user['username']}")
        return jsonify({'message': 'Service deleted successfully'})
        
    except Error as e:
        logger.error(f"Error deleting service: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- CONTACT MANAGEMENT ----

@app.route('/api/admin/contacts', methods=['GET'])
@token_required
def get_contacts():
    """Get all contact submissions"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM contact_submissions ORDER BY submitted_at DESC')
        contacts = cursor.fetchall()
        cursor.close()
        return jsonify(contacts)
    except Error as e:
        logger.error(f"Error fetching contacts: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/contacts/<int:id>/read', methods=['PUT'])
@token_required
def mark_contact_read(id):
    """Mark contact as read"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE contact_submissions SET is_read = TRUE WHERE id = %s', (id,))
        cursor.close()
        return jsonify({'message': 'Contact marked as read'})
    except Error as e:
        logger.error(f"Error marking contact: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/contacts/<int:id>', methods=['DELETE'])
@token_required
def delete_contact(id):
    """Delete contact submission"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM contact_submissions WHERE id = %s', (id,))
        cursor.close()
        return jsonify({'message': 'Contact deleted successfully'})
    except Error as e:
        logger.error(f"Error deleting contact: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ---- IMAGE UPLOAD ----

@app.route('/api/admin/upload', methods=['POST'])
@token_required
def upload_image():
    """Upload image file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add unique suffix
            filename = f"{filename.rsplit('.', 1)[0]}_{secrets.token_hex(4)}.{filename.rsplit('.', 1)[1]}"
            filepath = os.path.join(app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER), filename)
            file.save(filepath)
            
            logger.info(f"Image uploaded: {filename} by {request.current_user['username']}")
            return jsonify({
                'message': 'Image uploaded successfully',
                'url': f'/static/images/{filename}'
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return jsonify({'error': 'Upload failed'}), 500

# ---- CONTACT FORM (PUBLIC) ----

@app.route('/api/public/contact', methods=['POST'])
def submit_contact():
    """Public contact form submission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        name = sanitize_input(data.get('name', ''))
        email = sanitize_input(data.get('email', ''))
        phone = sanitize_input(data.get('phone', ''))
        message = sanitize_input(data.get('message', ''))

        if not name or not email or not message:
            return jsonify({'error': 'Name, email, and message are required'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO contact_submissions (name, email, phone, message) VALUES (%s, %s, %s, %s)',
                      (name, email, phone, message))
        cursor.close()
        
        logger.info(f"Contact form submitted by {name}")
        return jsonify({'message': 'Message sent successfully'})

    except Error as e:
        logger.error(f"Error submitting contact: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ═══════════════════════════════════════════════════════════
# STATIC FILE SERVING (Admin Panel)
# ═══════════════════════════════════════════════════════════

@app.route('/')
def serve_root():
    """Serve users.html from root"""
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..'), 'users.html')

@app.route('/admin')
def serve_admin_root():
    """Serve admin login page"""
    admin_folder = os.path.join(os.path.dirname(__file__), 'admin-dist')
    return send_from_directory(admin_folder, 'index.html')

@app.route('/admin/dashboard')
def serve_admin_dashboard():
    """Serve admin dashboard"""
    admin_folder = os.path.join(os.path.dirname(__file__), 'admin-dist')
    return send_from_directory(admin_folder, 'dashboard.html')

@app.route('/admin/<path:path>')
def serve_admin_static(path):
    """Serve admin panel static files"""
    admin_folder = os.path.join(os.path.dirname(__file__), 'admin-dist')
    return send_from_directory(admin_folder, path)

# ═══════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ═══════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  ANSH AIR COOL - Production Backend API")
    print("="*70)
    print("  [SECURE] JWT Authentication")
    print("  [SECURE] XSS & SQL Injection Protection")
    print("  [SECURE] Rate Limiting Enabled")
    print("="*70)
    print("  API Base: http://localhost:5500/api")
    print("  Admin Panel: http://localhost:5500/admin")
    print("  Login: admin / admin123")
    print("="*70 + "\n")
    
    init_db()
    app.run(debug=False, port=5500, host='127.0.0.1')
