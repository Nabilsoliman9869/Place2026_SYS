import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def fetch_talent_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Username, Password, Role FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment')")
    rows = cursor.fetchall()
    
    if rows:
        print("Found Talent Users:")
        for r in rows:
            print(f"User: {r.Username}, Pass: {r.Password}, Role: {r.Role}, ID: {r.UserID}")
    else:
        print("No Talent Users found. Creating one...")
        cursor.execute("INSERT INTO Users_1 (Username, Password, Role, Email) VALUES (?, ?, ?, ?)", 
                       ('TalentUser', '123', 'Talent', 'talent@place2026.com'))
        conn.commit()
        print("Created User: TalentUser, Pass: 123")

    conn.close()

if __name__ == '__main__':
    fetch_talent_users()
