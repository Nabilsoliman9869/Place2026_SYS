import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def force_fix():
    print("--- STARTING DB FIX (FORCE) ---")
    if not os.path.exists(CONFIG_FILE):
        print("Config file missing!")
        return

    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    username = config.get("username", "")
    password = config.get("password", "")
    
    # Use logic matching app.py
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    print(f"Connecting to {server} / {database}...")
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Columns to add
        columns_to_add = [
            ("InterestLevel", "NVARCHAR(50)"),
            ("Feedback", "NVARCHAR(MAX)"),
            ("NextFollowUpDate", "DATE"),
            ("CampaignID", "INT"),
            ("SoftSkills", "NVARCHAR(MAX)"),
            ("EnglishLevel", "NVARCHAR(50)"),
            ("IsReadyForMatching", "BIT DEFAULT 0")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                print(f"Adding {col_name}...", end=" ")
                cursor.execute(f"ALTER TABLE Candidates ADD {col_name} {col_type}")
                conn.commit()
                print("DONE.")
            except pyodbc.ProgrammingError as e:
                if "42S21" in str(e) or "Column names in each table must be unique" in str(e):
                    print("ALREADY EXISTS.")
                else:
                    print(f"ERROR: {e}")
            except Exception as e:
                print(f"ERROR: {e}")

        conn.close()
        print("--- FIX COMPLETED ---")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == '__main__':
    force_fix()
