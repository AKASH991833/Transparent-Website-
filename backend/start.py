"""
Ansh Air Cool Backend - Quick Start Script
"""
import os
import sys

# Kill any existing Flask processes
os.system('taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul')

print("="*60)
print("  Ansh Air Cool - Backend Server")
print("="*60)
print()

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check .env
if not os.path.exists('.env'):
    print("[ERROR] .env file not found!")
    print("Please create .env file first.")
    input("Press Enter to exit...")
    sys.exit(1)

print("[1/3] Environment OK")

# Check dependencies
try:
    import flask
    import mysql.connector
    from werkzeug.security import generate_password_hash
    print("[2/3] Dependencies OK")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Running: pip install -r requirements.txt")
    os.system('python -m pip install -r requirements.txt')

# Run app
print("[3/3] Starting server...")
print()
print("="*60)
print("  Server Starting...")
print("="*60)
print()
print("Website:  http://localhost:5000")
print("Admin:    http://localhost:5000/admin")
print()
print("Login:    admin / admin123")
print()
print("Press Ctrl+C to stop")
print("="*60)
print()

# Execute app.py
exec(open('app.py').read())
