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

def update_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Adding AvailabilityStatus Field...")

        # Candidates Table
        fields = [
            ("AvailabilityStatus", "NVARCHAR(50)")
        ]
        
        for col, dtype in fields:
            cursor.execute(f"""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Candidates' AND COLUMN_NAME='{col}')
                BEGIN
                    ALTER TABLE Candidates ADD {col} {dtype};
                    PRINT 'Added {col} to Candidates';
                END
            """)

        conn.commit()
        print(">>> Schema Updated Successfully.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    update_schema()
