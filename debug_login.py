import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def debug_users():
    print("--- LOGIN DEBUGGER ---")
    if not os.path.exists(CONFIG_FILE):
        print("Config file missing!")
        return

    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    print(f"Target Server: {config.get('server')}")
    print(f"Target DB: {config.get('database')}")
    
    # Force Driver 17 for testing (or 18 if you prefer)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("\nChecking Users Table...")
        cursor.execute("SELECT UserID, Username, Password, Role FROM Users")
        users = cursor.fetchall()
        
        if not users:
            print(">>> TABLE IS EMPTY! No users found. <<<")
        else:
            print(f">>> Found {len(users)} Users: <<<")
            print(f"{'ID':<5} {'Username':<20} {'Password':<20} {'Role':<15}")
            print("-" * 60)
            for u in users:
                # Use repr() to show hidden characters/spaces
                print(f"{u[0]:<5} {repr(u[1]):<20} {repr(u[2]):<20} {u[3]:<15}")
                
        conn.close()
        
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == '__main__':
    debug_users()
