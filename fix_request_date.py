import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

def check_and_fix_column():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Checking ClientRequests table structure...")
        
        # Check columns in ClientRequests
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ClientRequests'")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if 'RequestDate' not in columns:
            print(">>> 'RequestDate' missing. Adding it...")
            cursor.execute("ALTER TABLE ClientRequests ADD RequestDate DATETIME DEFAULT GETDATE()")
            cursor.commit()
            print(">>> Added 'RequestDate' successfully.")
        else:
            print(">>> 'RequestDate' already exists.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    check_and_fix_column()
