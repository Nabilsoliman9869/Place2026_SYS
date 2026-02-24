import pyodbc
import json
import os

def get_connection():
    config_path = 'db_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        print("Config file not found, using defaults.")
        config = {}
    
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};'
    
    print(f"Connecting to {server},{port}...")
    return pyodbc.connect(conn_str)

def update_schema():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Update Candidates Table
        print("Checking Candidates table...")
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Candidates'")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Current Candidates columns: {columns}")
        
        if 'Address' not in columns:
            print("Adding Address column...")
            cursor.execute("ALTER TABLE Candidates ADD Address NVARCHAR(255)")
            
        if 'Age' not in columns:
            print("Adding Age column...")
            cursor.execute("ALTER TABLE Candidates ADD Age INT")
            
        if 'WorkedHereBefore' not in columns:
            print("Adding WorkedHereBefore column...")
            cursor.execute("ALTER TABLE Candidates ADD WorkedHereBefore BIT DEFAULT 0")
            
        # Check for CreatedBy
        if 'CreatedBy' not in columns:
             if 'SalesAgentID' in columns:
                 print("SalesAgentID exists. We can use it as CreatedBy/RecruiterID.")
             else:
                 print("Adding CreatedBy column...")
                 cursor.execute("ALTER TABLE Candidates ADD CreatedBy INT")
        
        # 2. Update Schedules Table (Legacy/Interviews?)
        print("Checking Schedules table...")
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Schedules'")
        s_columns = [row[0] for row in cursor.fetchall()]
        print(f"Current Schedules columns: {s_columns}")
        
        if 'IsConfirmedByRecruiter' not in s_columns:
            print("Adding IsConfirmedByRecruiter column to Schedules...")
            cursor.execute("ALTER TABLE Schedules ADD IsConfirmedByRecruiter BIT DEFAULT 0")

        # 3. Update TASchedules Table (Talent Tests)
        print("Checking TASchedules table...")
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TASchedules'")
        ta_columns = [row[0] for row in cursor.fetchall()]
        print(f"Current TASchedules columns: {ta_columns}")
        
        if 'IsConfirmedByRecruiter' not in ta_columns:
            print("Adding IsConfirmedByRecruiter column to TASchedules...")
            cursor.execute("ALTER TABLE TASchedules ADD IsConfirmedByRecruiter BIT DEFAULT 0")
            
        conn.commit()
        print("Schema update completed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_schema()
