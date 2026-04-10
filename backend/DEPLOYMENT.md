# 🚀 ANSH AIR COOL - Complete Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Database Configuration](#database-configuration)
4. [Running the Application](#running-the-application)
5. [Admin Panel Access](#admin-panel-access)
6. [Security Notes](#security-notes)
7. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **MySQL 8.0+** - [Download](https://dev.mysql.com/downloads/mysql/)
- **Git** (optional) - [Download](https://git-scm.com/downloads)

### Verify Installation
```bash
python --version
mysql --version
```

---

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd "E:\Compress Fiels\Transparentui\Transparentui\backend"
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Edit the `.env` file in the backend directory:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=ac_service_billing
FLASK_SECRET_KEY=your_super_secret_key_here_change_this
JWT_SECRET_KEY=your_jwt_secret_key_change_this_to_something_random
```

**⚠️ IMPORTANT:** Change the secret keys to random strings for security!

---

## Database Configuration

### Automatic Database Setup
The application will automatically create the database and tables when you first run it.

### Manual Database Creation (Optional)
If you prefer to set up manually:

```sql
CREATE DATABASE ac_service_billing;

-- Use the database
USE ac_service_billing;

-- Tables will be created automatically by init_db()
```

### Default Data
The system will automatically seed:
- ✅ 1 admin user (username: `admin`, password: `admin123`)
- ✅ 3 sample products
- ✅ 6 sample services
- ✅ Default site settings
- ✅ Default hero settings
- ✅ 4 default marquee items

---

## Running the Application

### Development Mode
```bash
# From the backend directory
python app_api.py
```

The application will start on:
- **API Server**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Public API**: http://localhost:5000/api/public/*

### Verify Installation
Open your browser and visit:
1. http://localhost:5000/api/public/hero-data - Should return JSON
2. http://localhost:5000/admin - Admin login page

---

## Admin Panel Access

### Login Credentials
- **URL**: http://localhost:5000/admin
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT:** Change the password immediately after first login!

### Admin Panel Features
1. **Dashboard** - View statistics and overview
2. **Hero Section** - Edit hero text, stats, features
3. **Marquee Text** - Manage scrolling marquee items
4. **Products** - Add/Edit/Delete products
5. **Services** - Manage service offerings
6. **Site Settings** - Update contact info, address
7. **Contacts** - View contact form submissions

---

## Security Notes

### ✅ Implemented Security Features
1. **JWT Authentication** - Secure token-based auth
2. **Password Hashing** - Werkzeug's pbkdf2:sha256
3. **Rate Limiting** - Prevents brute force attacks
4. **XSS Protection** - Bleach library sanitizes all inputs
5. **SQL Injection Prevention** - Parameterized queries
6. **Input Validation** - Email, URL, and data validation

### 🔒 Security Recommendations
1. **Change Default Password** - Immediately after setup
2. **Use HTTPS** - In production, always use SSL
3. **Strong Secret Keys** - Use random 64+ character strings
4. **Environment Variables** - Never commit `.env` to version control
5. **Regular Updates** - Keep Python and dependencies updated
6. **Database Backups** - Regular automated backups

---

## Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app_api:app
```

### Using Waitress (Windows)
```bash
pip install waitress

waitress-serve --port=5000 app_api:app
```

### Nginx Configuration (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/backend/static;
        expires 30d;
    }
}
```

### Environment Variables for Production
```env
FLASK_ENV=production
FLASK_SECRET_KEY=super_long_random_string_here
JWT_SECRET_KEY=another_super_long_random_string
MYSQL_HOST=your_database_host
MYSQL_PORT=3306
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_DB=ac_service_billing
```

### Generate Secret Keys
```python
import secrets
print("FLASK_SECRET_KEY:", secrets.token_hex(64))
print("JWT_SECRET_KEY:", secrets.token_hex(64))
```

---

## API Endpoints Reference

### Public Endpoints (No Auth)
```
GET  /api/public/site-settings    - Get site settings
GET  /api/public/hero-data        - Get hero section data
GET  /api/public/marquee          - Get marquee items
GET  /api/public/products         - Get active products
GET  /api/public/services         - Get active services
POST /api/public/contact          - Submit contact form
```

### Admin Endpoints (JWT Auth Required)
```
POST /api/auth/login              - Admin login
GET  /api/admin/dashboard         - Dashboard stats
GET  /api/admin/hero              - Get hero settings
PUT  /api/admin/hero              - Update hero settings
GET  /api/admin/site-settings     - Get site settings
PUT  /api/admin/site-settings     - Update site settings
GET  /api/admin/marquee           - Get marquee items
POST /api/admin/marquee           - Create marquee item
PUT  /api/admin/marquee/:id       - Update marquee item
DELETE /api/admin/marquee/:id     - Delete marquee item
GET  /api/admin/products          - Get all products
POST /api/admin/products          - Create product
PUT  /api/admin/products/:id      - Update product
DELETE /api/admin/products/:id    - Delete product
GET  /api/admin/services          - Get all services
POST /api/admin/services          - Create service
PUT  /api/admin/services/:id      - Update service
DELETE /api/admin/services/:id    - Delete service
GET  /api/admin/contacts          - Get contacts
PUT  /api/admin/contacts/:id/read - Mark as read
DELETE /api/admin/contacts/:id    - Delete contact
POST /api/admin/upload            - Upload image
```

---

## Connecting users.html to Backend

### Option 1: Serve users.html from Flask
Move `users.html` to `backend/templates/index.html` and update the route in `app_api.py`:

```python
@app.route('/')
def index():
    return send_from_directory('../', 'users.html')
```

### Option 2: Use users.html as Static File
Add this to `app_api.py`:

```python
@app.route('/')
def index():
    return send_from_directory('../', 'users.html')
```

The `dynamic-loader.js` will automatically load all content from the API!

---

## Troubleshooting

### Database Connection Error
```
mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server
```
**Solution:**
1. Ensure MySQL is running
2. Check credentials in `.env`
3. Verify MySQL user has proper permissions

### Port Already in Use
```
OSError: [WinError 10048] Only one usage of each socket address
```
**Solution:**
Change port in `app_api.py`:
```python
app.run(debug=False, port=5001, host='127.0.0.1')
```

### Module Not Found
```
ModuleNotFoundError: No module named 'jwt'
```
**Solution:**
```bash
pip install -r requirements.txt
```

---

## Support

For issues or questions:
1. Check the logs: `logs/` directory (if configured)
2. Review error messages in console
3. Verify all environment variables are set correctly

---

## 🎉 You're All Set!

Your production-ready admin panel is now running. Access it at:
- **Admin Panel**: http://localhost:5000/admin
- **API Documentation**: See endpoints above

**Happy Managing!** 🚀
