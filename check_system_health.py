import pyodbc
import json
import os
import sys
import re

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

def check_health():
    print(">>> STARTING SYSTEM HEALTH CHECK <<<\n")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. SCHEMA VALIDATION
    print("--- 1. Checking Critical Columns ---")
    critical_checks = [
        ('Services', 'ServiceType'),
        ('Attendance', 'AttendanceDate'),
        ('Attendance', 'Date'),
        ('Candidates', 'SalesAgentID'),
        ('Candidates', 'HRCode'),
        ('Candidates', 'NationalID'),
        ('Users_1', 'Role'),
        ('Users_1', 'TeamWorkload') 
    ]
    
    for table, col in critical_checks:
        try:
            cursor.execute(f"SELECT TOP 1 {col} FROM {table}")
            print(f"[OK] {table}.{col} exists.")
        except:
            print(f"[MISSING] {table}.{col} NOT FOUND! (May cause crashes)")

    # 2. ROLE VALIDATION
    print("\n--- 2. Checking User Roles ---")
    cursor.execute("SELECT DISTINCT Role FROM Users_1")
    db_roles = [r[0] for r in cursor.fetchall()]
    print(f"Roles found in DB: {db_roles}")
    
    # Check if these roles are handled in app.py (Simple text scan)
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
        
    for role in db_roles:
        if role not in app_code:
            print(f"[WARNING] Role '{role}' exists in DB but might not be handled explicitly in app.py")
        else:
            print(f"[OK] Role '{role}' found in code.")

    # 3. ORPHANED DATA
    print("\n--- 3. Checking Orphaned Data ---")
    
    # Candidates without SalesAgent
    cursor.execute("SELECT COUNT(*) FROM Candidates WHERE SalesAgentID IS NULL")
    unassigned = cursor.fetchone()[0]
    print(f"Unassigned Candidates: {unassigned}")
    
    # Enrollments with invalid Batch
    cursor.execute("SELECT COUNT(*) FROM Enrollments WHERE BatchID NOT IN (SELECT BatchID FROM CourseBatches)")
    orphaned_enrollments = cursor.fetchone()[0]
    print(f"Orphaned Enrollments (Invalid Batch): {orphaned_enrollments}")

    print("\n>>> HEALTH CHECK COMPLETE <<<")

if __name__ == "__main__":
    check_health()
