import os
import json
import secrets
import mysql.connector
from mysql.connector import Error
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ansh_aircool_secret_2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'ac_service_billing'),
            dictionary=True
        )
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{os.getenv('MYSQL_DB', 'ac_service_billing')}`")
        cursor.close()
        conn.close()
        
        db = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'ac_service_billing'),
            dictionary=True
        )
        c = db.cursor(dictionary=True)
        
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL, buy_price DECIMAL(10,2) NOT NULL,
            rent_price DECIMAL(10,2) NOT NULL, old_price DECIMAL(10,2),
            description_buy TEXT, description_rent TEXT, image VARCHAR(255),
            rating DECIMAL(2,1) DEFAULT 4.5, rating_count INT DEFAULT 0,
            badge VARCHAR(50), features JSON, is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(100) NOT NULL,
            description TEXT, image VARCHAR(255), icon VARCHAR(50),
            features JSON, order_index INT DEFAULT 0, is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS admin_users (
            id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, email VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS contact_submissions (
            id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL, phone VARCHAR(20), message TEXT,
            is_read BOOLEAN DEFAULT FALSE, submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS site_settings (
            id INT AUTO_INCREMENT PRIMARY KEY, site_name VARCHAR(100),
            phone VARCHAR(20), email VARCHAR(100), address TEXT,
            whatsapp_number VARCHAR(20), years_experience INT,
            customers_served INT, satisfaction_rate INT
        )''')
        
        c.execute('SELECT COUNT(*) as cnt FROM admin_users')
        if c.fetchone()['cnt'] == 0:
            c.execute('INSERT INTO admin_users (username, password, email) VALUES (%s, %s, %s)',
                ('admin', generate_password_hash('admin123'), 'admin@anshaircool.com'))
        
        c.execute('SELECT COUNT(*) as cnt FROM products')
        if c.fetchone()['cnt'] == 0:
            for p in [
                ('Ansh Pro Cool Split', 'Split AC', 42999, 2499, 52999, 'Premium 5-star inverter split AC', 'Rent this premium split AC', '/static/images/split-ac.jpg', 4.5, 2847, 'best-seller', '["5 Star", "Inverter", "Cool"]'),
                ('Ansh Elite Window', 'Window AC', 32499, 1799, 38999, 'Energy-efficient 4-star window AC', 'Affordable window AC rental', '/static/images/window-ac.jpg', 5.0, 1523, 'new', '["4 Star", "Auto", "Easy Install"]'),
                ('Ansh Max Inverter Pro', 'Inverter AC', 54999, 3299, 68999, 'Top-of-the-line 5-star inverter AC', 'Premium cassette AC on rent', '/static/images/cassette-ac.jpg', 5.0, 3291, 'hot', '["5 Star", "Variable", "Auto Clean"]')
            ]:
                c.execute('INSERT INTO products (name,category,buy_price,rent_price,old_price,description_buy,description_rent,image,rating,rating_count,badge,features) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', p)
        
        c.execute('SELECT COUNT(*) as cnt FROM services')
        if c.fetchone()['cnt'] == 0:
            for i, s in enumerate([
                ('AC Installation', 'Professional setup for all AC types', '/static/images/ac-installation.jpg', 'fa-screwdriver-wrench', '["Expert Technicians", "All Brands", "Same Day"]'),
                ('AC Cleaning', 'Deep cleaning with anti-bacterial wash', '/static/images/ac-cleaning.jpg', 'fa-broom', '["Foam Wash", "Deep Cleaning", "Anti-Bacterial"]'),
                ('Gas Refill', 'R410A & R32 gas with leak detection', '/static/images/gas-refill.jpg', 'fa-snowflake', '["Genuine Gas", "Leak Detection", "Pressure Test"]'),
                ('AC Repair', 'Same-day repair with genuine parts', '/static/images/ac-repair.jpg', 'fa-wrench', '["All Brands", "Genuine Parts", "30-Day Warranty"]'),
                ('AMC Service', 'Yearly maintenance with priority support', '/static/images/amc-service.jpg', 'fa-clipboard-check', '["Unlimited Calls", "Priority Support", "20% Discount"]'),
                ('PCB Repair', 'Component level repair for inverters', '/static/images/pcb-repair.jpg', 'fa-microchip', '["Component Repair", "Inverter Specialist", "90-Day Warranty"]')
            ], 1):
                c.execute('INSERT INTO services (title,description,image,icon,features,order_index) VALUES (%s,%s,%s,%s,%s,%s)', (*s, i))
        
        c.execute('SELECT COUNT(*) as cnt FROM site_settings')
        if c.fetchone()['cnt'] == 0:
            c.execute('INSERT INTO site_settings (site_name,phone,email,address,whatsapp_number,years_experience,customers_served,satisfaction_rate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                ('ANSH AIR COOL', '+919876543210', 'support@anshaircool.com', 'Mumbai, India', '919876543210', 15, 50000, 99))
        
        db.commit()
        c.close()
        db.close()
        print("Database initialized successfully!")
    except Error as e:
        print(f"DB Init Error: {e}")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ROUTES
@app.route('/')
def index():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM products WHERE is_active=TRUE ORDER BY id')
    products = c.fetchall()
    c.execute('SELECT * FROM services WHERE is_active=TRUE ORDER BY order_index')
    services = c.fetchall()
    c.execute('SELECT * FROM site_settings LIMIT 1')
    settings = c.fetchone() or {}
    c.close()
    return render_template('index.html', products=products, services=services, settings=settings)

@app.route('/admin')
def admin_login():
    if 'admin' in session: return redirect(url_for('dashboard'))
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def login_post():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM admin_users WHERE username=%s AND is_active=TRUE', (request.form['username'],))
    user = c.fetchone()
    c.close()
    if user and check_password_hash(user['password'], request.form['password']):
        session['admin'] = True
        session['username'] = user['username']
        session.permanent = True
        return redirect(url_for('dashboard'))
    flash('Invalid credentials', 'error')
    return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def dashboard():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT COUNT(*) as n FROM products'); pc = c.fetchone()['n']
    c.execute('SELECT COUNT(*) as n FROM services'); sc = c.fetchone()['n']
    c.execute('SELECT COUNT(*) as n FROM contact_submissions'); cc = c.fetchone()['n']
    c.execute('SELECT COUNT(*) as n FROM contact_submissions WHERE is_read=FALSE'); uc = c.fetchone()['n']
    c.close()
    return render_template('admin/dashboard.html', pc=pc, sc=sc, cc=cc, uc=uc)

@app.route('/admin/products')
@login_required
def products():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM products ORDER BY id DESC')
    return render_template('admin/products.html', products=c.fetchall())

@app.route('/admin/products/add', methods=['GET','POST'])
@login_required
def add_product():
    if request.method == 'POST':
        db = get_db()
        c = db.cursor()
        img = '/static/images/split-ac.jpg'
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                fn = secure_filename(f.filename)
                fn = f"{fn.rsplit('.',1)[0]}_{secrets.token_hex(3)}.{fn.rsplit('.',1)[1]}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                img = fn
        c.execute('INSERT INTO products (name,category,buy_price,rent_price,old_price,description_buy,description_rent,image,badge,features) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (request.form['name'], request.form['category'], request.form['buy_price'], request.form['rent_price'],
             request.form.get('old_price',0), request.form['description_buy'], request.form['description_rent'],
             img, request.form.get('badge',''), json.dumps(request.form.getlist('features[]'))))
        db.commit()
        return redirect(url_for('products'))
    return render_template('admin/product_form.html')

@app.route('/admin/products/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_product(id):
    db = get_db()
    if request.method == 'POST':
        c = db.cursor()
        c.execute('UPDATE products SET name=%s,category=%s,buy_price=%s,rent_price=%s,old_price=%s,description_buy=%s,description_rent=%s,badge=%s,features=%s WHERE id=%s',
            (request.form['name'], request.form['category'], request.form['buy_price'], request.form['rent_price'],
             request.form.get('old_price',0), request.form['description_buy'], request.form['description_rent'],
             request.form.get('badge',''), json.dumps(request.form.getlist('features[]')), id))
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                fn = f"{f.filename.rsplit('.',1)[0]}_{secrets.token_hex(3)}.{f.filename.rsplit('.',1)[1]}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db.cursor().execute('UPDATE products SET image=%s WHERE id=%s', (fn, id))
        db.commit()
        return redirect(url_for('products'))
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM products WHERE id=%s', (id,))
    return render_template('admin/product_form.html', product=c.fetchone())

@app.route('/admin/products/delete/<int:id>')
@login_required
def delete_product(id):
    db = get_db()
    db.cursor().execute('DELETE FROM products WHERE id=%s', (id,))
    db.commit()
    return redirect(url_for('products'))

@app.route('/admin/services')
@login_required
def services():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM services ORDER BY order_index')
    return render_template('admin/services.html', services=c.fetchall())

@app.route('/admin/services/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_service(id):
    db = get_db()
    if request.method == 'POST':
        c = db.cursor()
        c.execute('UPDATE services SET title=%s,description=%s,order_index=%s,features=%s WHERE id=%s',
            (request.form['title'], request.form['description'], request.form['order_index'],
             json.dumps(request.form.getlist('features[]')), id))
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                fn = f"{f.filename.rsplit('.',1)[0]}_{secrets.token_hex(3)}.{f.filename.rsplit('.',1)[1]}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db.cursor().execute('UPDATE services SET image=%s WHERE id=%s', (fn, id))
        db.commit()
        return redirect(url_for('services'))
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM services WHERE id=%s', (id,))
    return render_template('admin/service_form.html', service=c.fetchone())

@app.route('/admin/contacts')
@login_required
def contacts():
    db = get_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM contact_submissions ORDER BY submitted_at DESC')
    return render_template('admin/contacts.html', contacts=c.fetchall())

@app.route('/admin/contacts/mark/<int:id>')
@login_required
def mark_read(id):
    db = get_db()
    db.cursor().execute('UPDATE contact_submissions SET is_read=TRUE WHERE id=%s', (id,))
    db.commit()
    return redirect(url_for('contacts'))

@app.route('/admin/contacts/delete/<int:id>')
@login_required
def delete_contact(id):
    db = get_db()
    db.cursor().execute('DELETE FROM contact_submissions WHERE id=%s', (id,))
    db.commit()
    return redirect(url_for('contacts'))

@app.route('/contact/submit', methods=['POST'])
def contact_submit():
    db = get_db()
    db.cursor().execute('INSERT INTO contact_submissions (name,email,message) VALUES (%s,%s,%s)',
        (request.form.get('name',''), request.form.get('email',''), request.form.get('message','')))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("  Ansh Air Cool Backend")
    print("="*60)
    print("  Website: http://localhost:5000")
    print("  Admin:   http://localhost:5000/admin")
    print("  Login:   admin / admin123")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')
