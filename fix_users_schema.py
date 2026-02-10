import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def fix_users_table():
    print("Fixing Users Table...")
    if not os.path.exists(CONFIG_FILE): return
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Add FullName column if not exists
        try:
            cursor.execute("ALTER TABLE Users ADD FullName NVARCHAR(100)")
            conn.commit()
            print("Added FullName column.")
        except Exception as e:
            print(f"Column might exist: {e}")

        # Add Email column if not exists
        try:
            cursor.execute("ALTER TABLE Users ADD Email NVARCHAR(100)")
            conn.commit()
            print("Added Email column.")
        except: pass

        conn.close()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == '__main__':
    fix_users_table()
