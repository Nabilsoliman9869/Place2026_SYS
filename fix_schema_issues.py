import pyodbc
import json
import os
import sys

# --- CONFIG ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(application_path, 'db_config.json')

def get_db_connection():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def fix_schema():
    print(">>> FIXING SCHEMA ISSUES <<<")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Add ServiceType to Services
    try:
        print("Checking Services.ServiceType...")
        cursor.execute("SELECT TOP 1 ServiceType FROM Services")
        print(" - Exists.")
    except:
        print(" - Missing. Adding column...")
        cursor.execute("ALTER TABLE Services ADD ServiceType NVARCHAR(50) DEFAULT 'General'")
        cursor.execute("UPDATE Services SET ServiceType = 'General'")
        conn.commit()
        print(" - Added and populated.")

    # 2. Rename Date to AttendanceDate in Attendance? 
    # Actually, it's better to keep 'Date' if it works, but 'AttendanceDate' is more descriptive.
    # Let's just leave it as 'Date' but ensure app.py uses it.
    
    print(">>> SCHEMA FIX COMPLETE <<<")

if __name__ == "__main__":
    fix_schema()
