import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def list_allocation_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    print(f"{'Username':<20} {'Password':<15} {'Role':<25} {'FullName'}")
    print("-" * 80)
    
    cursor.execute("SELECT Username, Password, Role, FullName FROM Users_1 WHERE Role IN ('Allocator', 'AllocationSpecialist', 'AllocationManager') ORDER BY Role")
    
    for row in cursor.fetchall():
        print(f"{row.Username:<20} {row.Password:<15} {row.Role:<25} {row.FullName}")

    conn.close()

if __name__ == '__main__':
    list_allocation_users()
