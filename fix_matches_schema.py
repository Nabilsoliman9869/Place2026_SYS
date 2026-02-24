import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def fix_matches_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    print("Checking 'Matches' table schema...")
    
    # 1. Check/Add AllocatorID
    try:
        cursor.execute("SELECT AllocatorID FROM Matches WHERE 1=0")
        print("Column 'AllocatorID' exists.")
    except pyodbc.Error:
        print("Column 'AllocatorID' missing. Adding it...")
        cursor.execute("ALTER TABLE Matches ADD AllocatorID INT NULL")
        conn.commit()
        print(">>> Added 'AllocatorID'.")

    # 2. Check/Add ReviewNotes
    try:
        cursor.execute("SELECT ReviewNotes FROM Matches WHERE 1=0")
        print("Column 'ReviewNotes' exists.")
    except pyodbc.Error:
        print("Column 'ReviewNotes' missing. Adding it...")
        cursor.execute("ALTER TABLE Matches ADD ReviewNotes NVARCHAR(MAX) NULL")
        conn.commit()
        print(">>> Added 'ReviewNotes'.")

    conn.close()

if __name__ == '__main__':
    fix_matches_table()
