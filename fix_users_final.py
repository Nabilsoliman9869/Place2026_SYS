import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def fix_users_final():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    # 1. Fix 'adl_rec'
    print("\n--- Checking 'adl_rec' ---")
    cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Username = 'adl_rec'")
    row = cursor.fetchone()
    
    if row:
        print(f"User 'adl_rec' found (ID: {row.UserID}). Resetting password...")
        cursor.execute("UPDATE Users_1 SET Password='123' WHERE Username='adl_rec'")
        conn.commit()
        print(">>> Password for 'adl_rec' is set to '123'.")
    else:
        print("User 'adl_rec' NOT found. Creating it...")
        try:
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName, Email) VALUES (?, ?, ?, ?, ?)", 
                           ('adl_rec', '123', 'Recruiter', 'Adel Recruiter', 'adel@place2026.com'))
            conn.commit()
            print(">>> User 'adl_rec' created successfully.")
        except Exception as e:
            print(f"Error creating adl_rec: {e}")

    # 2. Fix 'mennatalla'
    print("\n--- Checking 'mennatalla' ---")
    cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Username = 'mennatalla'")
    row = cursor.fetchone()
    
    if row:
        print(f"User 'mennatalla' found (ID: {row.UserID}, Role: {row.Role}). Resetting password...")
        cursor.execute("UPDATE Users_1 SET Password='123' WHERE Username='mennatalla'")
        conn.commit()
        print(">>> Password for 'mennatalla' is set to '123'.")
    else:
        print("User 'mennatalla' NOT found. Creating it...")
        try:
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, ?, ?, ?)", 
                           ('mennatalla', '123', 'Talent', 'Mennatalla Talent'))
            conn.commit()
            print(">>> User 'mennatalla' created successfully.")
        except Exception as e:
            print(f"Error creating mennatalla: {e}")

    conn.close()

if __name__ == '__main__':
    fix_users_final()
