import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def fix_adl_user():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    # Check for 'adl'
    print("Checking for username 'adl'...")
    cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Username LIKE '%adl%'")
    rows = cursor.fetchall()
    found_exact = False
    
    for r in rows:
        print(f"Found similar: ID={r.UserID}, User={r.Username}, Role={r.Role}")
        if r.Username == 'adl':
            found_exact = True
            
    if not found_exact:
        print("User 'adl' NOT found. Creating it now...")
        try:
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName, Email) VALUES (?, ?, ?, ?, ?)", 
                           ('adl', '123', 'Recruiter', 'Adl Recruiter', 'adl@example.com'))
            conn.commit()
            print(">>> User 'adl' created successfully with password '123'.")
        except Exception as e:
            print(f"Error creating user: {e}")
    else:
        print("User 'adl' exists. Resetting password to '123' to be sure.")
        cursor.execute("UPDATE Users_1 SET Password='123' WHERE Username='adl'")
        conn.commit()
        print(">>> Password for 'adl' reset to '123'.")

    conn.close()

if __name__ == '__main__':
    fix_adl_user()
