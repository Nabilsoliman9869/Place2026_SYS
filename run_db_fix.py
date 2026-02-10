import pyodbc
import json
import os

# Config path is in the other directory
CONFIG_FILE = r'E:\Place _trae\db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found at {CONFIG_FILE}")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def run_fix():
    print("Loading config...")
    config = load_config()
    if not config: 
        print("Failed to load config.")
        return

    print(f"Connecting to database {config.get('database')} on {config.get('server')}...")
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        sqls = [
            """IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Clients'))
               ALTER TABLE Clients ADD CreatedAt DATETIME DEFAULT GETDATE();""",
               
            """IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'ClientRequests'))
               ALTER TABLE ClientRequests ADD CreatedAt DATETIME DEFAULT GETDATE();""",
               
            """IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Campaigns'))
               ALTER TABLE Campaigns ADD CreatedAt DATETIME DEFAULT GETDATE();""",
               
            """IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Candidates'))
               ALTER TABLE Candidates ADD CreatedAt DATETIME DEFAULT GETDATE();"""
        ]

        print("Applying fixes...")
        for sql in sqls:
            try:
                cursor.execute(sql)
                conn.commit()
                print("Executed column check/add.")
            except Exception as e:
                print(f"Error executing SQL: {e}")
        
        print("Fix applied successfully.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_fix()
