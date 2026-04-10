"""
Database Backup Utility
Usage: python backup_db.py
"""
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def backup_database():
    """Create a backup of the MySQL database"""
    
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', '')
    mysql_db = os.getenv('MYSQL_DB', 'ac_service_billing')
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    
    # Create backup directory
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'{mysql_db}_{timestamp}.sql')
    
    print(f"Creating backup: {backup_file}")
    
    # Build mysqldump command
    cmd = f'mysqldump -h {mysql_host} -u {mysql_user}'
    if mysql_password:
        cmd += f' -p{mysql_password}'
    cmd += f' {mysql_db} > "{backup_file}"'
    
    # Execute backup
    try:
        os.system(cmd)
        
        if os.path.exists(backup_file):
            file_size = os.path.getsize(backup_file) / 1024  # KB
            print(f"✓ Backup created successfully!")
            print(f"  File: {backup_file}")
            print(f"  Size: {file_size:.2f} KB")
        else:
            print("✗ Backup failed!")
            
    except Exception as e:
        print(f"✗ Backup error: {str(e)}")

if __name__ == '__main__':
    print("=" * 50)
    print("  Database Backup Utility")
    print("=" * 50)
    print()
    backup_database()
    print()
    input("Press Enter to exit...")
