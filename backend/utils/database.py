import json
from flask import current_app

class DatabaseManager:
    """Database utility functions"""
    
    @staticmethod
    def init_db(mysql):
        """Initialize database with tables and default data"""
        conn = mysql.connection
        cursor = conn.cursor()
        
        # Create tables
        DatabaseManager._create_tables(cursor)
        
        # Insert default data
        DatabaseManager._insert_default_data(cursor)
        
        conn.commit()
        cursor.close()
    
    @staticmethod
    def _create_tables(cursor):
        """Create all necessary tables"""
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                buy_price DECIMAL(10, 2) NOT NULL,
                rent_price DECIMAL(10, 2) NOT NULL,
                old_price DECIMAL(10, 2),
                description_buy TEXT,
                description_rent TEXT,
                image VARCHAR(255),
                rating DECIMAL(2, 1) DEFAULT 4.5,
                rating_count INT DEFAULT 0,
                badge VARCHAR(50),
                features JSON,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                image VARCHAR(255),
                icon VARCHAR(50),
                features JSON,
                order_index INT DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_order (order_index),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_read (is_read),
                INDEX idx_date (submitted_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hero_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title_line1 VARCHAR(100),
                title_line2 VARCHAR(100),
                title_line3 VARCHAR(100),
                subtitle TEXT,
                image VARCHAR(255),
                starting_price DECIMAL(10, 2),
                old_price DECIMAL(10, 2),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                site_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                whatsapp_number VARCHAR(20),
                years_experience INT,
                customers_served INT,
                satisfaction_rate INT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
    
    @staticmethod
    def _insert_default_data(cursor):
        """Insert default data if tables are empty"""
        
        # Default admin user
        from utils.security import SecurityUtils
        
        cursor.execute('SELECT COUNT(*) as count FROM admin_users')
        result = cursor.fetchone()
        if result['count'] == 0:
            hashed_password = SecurityUtils.hash_password('admin123')
            cursor.execute(
                'INSERT INTO admin_users (username, password, email) VALUES (%s, %s, %s)',
                ('admin', hashed_password, 'admin@anshaircool.com')
            )
        
        # Default hero settings
        cursor.execute('SELECT COUNT(*) as count FROM hero_settings')
        result = cursor.fetchone()
        if result['count'] == 0:
            cursor.execute('''
                INSERT INTO hero_settings (title_line1, title_line2, title_line3, subtitle, image, starting_price, old_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', ('Experience', 'Ultimate Cooling', 'Like Never Before',
                  'Advanced inverter technology that saves up to 60% electricity while delivering lightning-fast cooling.',
                  '/static/images/split-ac.jpg', 32499, 38999))
        
        # Default site settings
        cursor.execute('SELECT COUNT(*) as count FROM site_settings')
        result = cursor.fetchone()
        if result['count'] == 0:
            cursor.execute('''
                INSERT INTO site_settings (site_name, phone, email, address, whatsapp_number, years_experience, customers_served, satisfaction_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', ('ANSH AIR COOL', '+919876543210', 'support@anshaircool.com',
                  '123 Cool Street, AC Market, Mumbai, Maharashtra', '919876543210', 15, 50000, 99))
        
        # Default products
        cursor.execute('SELECT COUNT(*) as count FROM products')
        result = cursor.fetchone()
        if result['count'] == 0:
            products = [
                ('Ansh Pro Cool Split', 'Split AC', 42999, 2499, 52999,
                 'Premium 5-star inverter split AC with advanced cooling technology. Perfect for homes and offices with energy savings up to 60%. Comes with 10-year compressor warranty and free installation.',
                 'Rent this premium split AC for your space. Includes free maintenance, 24/7 support, and no deposit required. Flexible rental terms with easy upgrade options.',
                 '/static/images/split-ac.jpg', 4.5, 2847, 'best-seller',
                 json.dumps(["5 Star", "Inverter", "Cool"])),

                ('Ansh Elite Window', 'Window AC', 32499, 1799, 38999,
                 'Energy-efficient 4-star window AC with quick cooling and auto mode. Easy installation, low noise operation. Perfect for bedrooms and small rooms with durable build quality.',
                 'Affordable window AC rental solution. Complete maintenance included. Great for rented apartments, offices, and seasonal needs. Quick installation within 24 hours.',
                 '/static/images/window-ac.jpg', 5.0, 1523, 'new',
                 json.dumps(["4 Star", "Auto", "Easy Install"])),

                ('Ansh Max Inverter Pro', 'Inverter AC', 54999, 3299, 68999,
                 'Top-of-the-line 5-star inverter AC with variable speed compressor. Ultra-quiet operation, auto-clean feature, and maximum energy efficiency. Best for large rooms and commercial spaces.',
                 'Premium cassette AC on rent for large spaces. Includes quarterly maintenance, priority support, and flexible upgrade options. Perfect for offices, shops, and large rooms.',
                 '/static/images/cassette-ac.jpg', 5.0, 3291, 'hot',
                 json.dumps(["5 Star", "Variable", "Auto Clean"]))
            ]
            
            for product in products:
                cursor.execute('''
                    INSERT INTO products (name, category, buy_price, rent_price, old_price, 
                                        description_buy, description_rent, image, rating, 
                                        rating_count, badge, features)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', product)
        
        # Default services
        cursor.execute('SELECT COUNT(*) as count FROM services')
        result = cursor.fetchone()
        if result['count'] == 0:
            services = [
                ('AC Installation', 'Professional setup for Split, Window & Cassette ACs with zero damage guarantee and free demo.',
                 '/static/images/ac-installation.jpg', 'fa-screwdriver-wrench',
                 json.dumps(["Expert Technicians", "All Brands Supported", "Same Day Service"]), 1),

                ('AC Cleaning & Service', 'Deep cleaning with anti-bacterial foam wash for better cooling and healthy air quality.',
                 '/static/images/ac-cleaning.jpg', 'fa-broom',
                 json.dumps(["Foam Wash Technology", "Filter Deep Cleaning", "Anti-Bacterial Treatment"]), 2),

                ('Gas Refill & Charging', 'R410A & R32 gas refill with leak detection and pressure testing for optimal cooling.',
                 '/static/images/gas-refill.jpg', 'fa-snowflake',
                 json.dumps(["Genuine Gas Only", "Leak Detection", "Pressure Testing"]), 3),

                ('AC Repair & Service', 'Same-day repair for all AC brands with genuine spare parts and service warranty.',
                 '/static/images/ac-repair.jpg', 'fa-wrench',
                 json.dumps(["All Brands Repaired", "Genuine Spare Parts", "30-Day Warranty"]), 4),

                ('Annual Maintenance (AMC)', 'Yearly AMC plans with unlimited servicing, priority support & 20% discount on repairs.',
                 '/static/images/amc-service.jpg', 'fa-clipboard-check',
                 json.dumps(["Unlimited Service Calls", "Priority Support", "20% Discount on Repairs"]), 5),

                ('PCB Repair & Service', 'Advanced PCB level repair for inverter ACs with component replacement and testing.',
                 '/static/images/pcb-repair.jpg', 'fa-microchip',
                 json.dumps(["Component Level Repair", "Inverter AC Specialist", "90-Day Warranty"]), 6)
            ]
            
            for service in services:
                cursor.execute('''
                    INSERT INTO services (title, description, image, icon, features, order_index)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', service)
