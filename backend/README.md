# Ansh Air Cool - Backend

Python Flask + MySQL backend for managing the Ansh Air Cool website.

## 📁 Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
├── utils/
│   ├── __init__.py
│   ├── security.py      # Security utilities
│   └── database.py      # Database utilities
├── static/
│   └── images/          # Uploaded images
└── templates/
    └── admin/           # Admin panel templates
        ├── base.html
        ├── login.html
        ├── dashboard.html
        ├── products.html
        ├── product_form.html
        ├── services.html
        ├── service_form.html
        └── contacts.html
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Installation

1. **Install dependencies:**
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. **Configure environment:**
   Edit `.env` file with your database credentials:
   ```env
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=ac_service_billing
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - **Website:** http://localhost:5000
   - **Admin Panel:** http://localhost:5000/admin

## 🔐 Default Admin Credentials

- **Username:** admin
- **Password:** admin123

**⚠️ IMPORTANT:** Change these credentials immediately after first login!

## 🗄️ Database

The database and tables are created automatically on first run.

**Database name:** `ac_service_billing`

**Tables:**
- `products` - AC products with buy/rent prices
- `services` - Services offered
- `admin_users` - Admin user accounts
- `contact_submissions` - Customer inquiries
- `hero_settings` - Hero section configuration
- `site_settings` - General site settings

## 🔒 Security Features

- ✅ Password hashing (PBKDF2-SHA256)
- ✅ Session management with timeout
- ✅ Input sanitization (XSS protection)
- ✅ File upload validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ CSRF token generation
- ✅ Secure session cookies
- ✅ Email & phone validation
- ✅ Price validation

## 📝 API Endpoints

### Public Routes
- `GET /` - Homepage
- `POST /contact/submit` - Submit contact form

### Admin Routes
- `GET /admin` - Admin login page
- `POST /admin/login` - Process login
- `GET /admin/logout` - Logout
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/products` - List products
- `GET/POST /admin/products/add` - Add product
- `GET/POST /admin/products/edit/<id>` - Edit product
- `GET /admin/products/delete/<id>` - Delete product
- `GET /admin/services` - List services
- `GET/POST /admin/services/edit/<id>` - Edit service
- `GET /admin/contacts` - View contacts
- `GET /admin/contacts/mark_read/<id>` - Mark as read
- `GET /admin/contacts/delete/<id>` - Delete contact

## 🛡️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_SECRET_KEY | Secret key for sessions | (required) |
| MYSQL_HOST | MySQL host | localhost |
| MYSQL_PORT | MySQL port | 3306 |
| MYSQL_USER | MySQL username | root |
| MYSQL_PASSWORD | MySQL password | (required) |
| MYSQL_DB | Database name | ac_service_billing |
| MAX_CONTENT_LENGTH | Max upload size (bytes) | 16777216 (16MB) |
| PERMANENT_SESSION_LIFETIME | Session timeout (seconds) | 7200 (2 hours) |

## 📦 Dependencies

- Flask 2.3.3 - Web framework
- Flask-MySQLdb 1.0.1 - MySQL connector
- Werkzeug 2.3.7 - Security utilities
- python-dotenv 1.0.0 - Environment variables
- Pillow 10.0.0 - Image processing

## 🚀 Deployment

### Production Checklist

- [ ] Change default admin password
- [ ] Update `.env` with production values
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `FLASK_SECRET_KEY`
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Use production database credentials
- [ ] Set up SSL certificate (HTTPS)
- [ ] Configure proper web server (Nginx/Apache)
- [ ] Set up backup strategy

### Using Gunicorn (Production WSGI)

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## 🐛 Troubleshooting

### MySQL Connection Error
- Ensure MySQL service is running
- Check credentials in `.env` file
- Verify database exists

### Module Not Found
```bash
python -m pip install -r requirements.txt
```

### Permission Denied
- Check folder permissions for `static/images/`
- Ensure upload directory exists

## 📄 License

Private - Ansh Air Cool

## 👨‍💻 Support

For issues or questions, contact: support@anshaircool.com
