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

def fix_sales_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(">>> Checking GeneralSales Schema...")
        
        # Check if CandidateID column exists in GeneralSales
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'GeneralSales' AND COLUMN_NAME = 'CandidateID'
        """)
        if cursor.fetchone()[0] == 0:
            print(">>> Column 'CandidateID' missing in GeneralSales. Adding it...")
            cursor.execute("ALTER TABLE GeneralSales ADD CandidateID INT NULL")
            print(">>> Column 'CandidateID' added successfully.")
        else:
            print(">>> Column 'CandidateID' already exists.")

        conn.commit()
        print(">>> Schema Fix Complete.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    fix_sales_schema()
