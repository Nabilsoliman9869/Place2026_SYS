
import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found")
        return None
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    conn_str = ""
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    
    return pyodbc.connect(conn_str)

def list_users():
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT Username, Role, Email FROM Users_1 ORDER BY Role, Username")
    users = cursor.fetchall()
    
    print(f"{'Username':<20} | {'Role':<25} | {'Email'}")
    print("-" * 60)
    for u in users:
        print(f"{u.Username:<20} | {u.Role:<25} | {u.Email}")
        
    conn.close()

if __name__ == "__main__":
    list_users()
