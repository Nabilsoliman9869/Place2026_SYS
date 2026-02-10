import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def add_fullname_column():
    if not os.path.exists(CONFIG_FILE): return
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Add FullName if not exists
        try:
            cursor.execute("ALTER TABLE Users ADD FullName NVARCHAR(100)")
            conn.commit()
            print("Added FullName column successfully.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == '__main__':
    add_fullname_column()
