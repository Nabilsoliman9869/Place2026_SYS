import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'
OUTPUT_FILE = r'E:\Place_2026_SYS\users_list.txt'

def list_users():
    if not os.path.exists(CONFIG_FILE): return
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        with open(OUTPUT_FILE, 'w') as f:
            f.write("--- SYSTEM USERS ---\n")
            cursor.execute("SELECT Username, Password, Role FROM Users")
            rows = cursor.fetchall()
            if not rows:
                f.write("No users found!\n")
            for row in rows:
                f.write(f"User: {row.Username} | Pass: {row.Password} | Role: {row.Role}\n")
            f.write("--------------------\n")
        
        conn.close()
    except Exception as e:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(f"Error: {e}")

if __name__ == '__main__':
    list_users()
