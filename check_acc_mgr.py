
import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def check_user():
    conn = get_db_connection()
    if not conn:
        print("DB Connection Failed")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT Username, Password, Role FROM Users_1 WHERE Username = 'acc_mgr'")
    user = cursor.fetchone()
    
    if user:
        print(f"User Found: {user.Username}, Role: '{user.Role}', Password: '{user.Password}'")
    else:
        print("User 'acc_mgr' NOT FOUND in database.")
        
    conn.close()

if __name__ == "__main__":
    check_user()
