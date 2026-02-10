import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def list_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Username, Password, Role, FullName FROM Users_1 ORDER BY Role, Username")
    
    print(f"{'ID':<5} {'Username':<20} {'Password':<15} {'Role':<20} {'FullName'}")
    print("-" * 80)
    
    for row in cursor.fetchall():
        print(f"{row.UserID:<5} {row.Username:<20} {row.Password:<15} {row.Role:<20} {row.FullName}")

    conn.close()

if __name__ == '__main__':
    list_users()
