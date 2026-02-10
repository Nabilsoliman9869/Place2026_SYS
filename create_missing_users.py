
import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def create_users():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    users_to_create = [
        ('acc_mgr', '123', 'AccountManager'),
        ('sara_alloc', '123', 'AllocationSpecialist'),
        ('rec_mgr', '123', 'RecruitmentManager') # Ensure this one too
    ]
    
    for user, pwd, role in users_to_create:
        # Check if exists
        cursor.execute("SELECT COUNT(*) FROM Users_1 WHERE Username = ?", (user,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role) VALUES (?, ?, ?)", (user, pwd, role))
            print(f"Created User: {user} ({role})")
        else:
            print(f"User {user} already exists.")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_users()
