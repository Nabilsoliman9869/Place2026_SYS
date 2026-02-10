import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

def fix_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(">>> Fixing User Passwords and Roles...")
        
        # 1. Update Passwords
        cursor.execute("UPDATE Users_1 SET Password = '123'")
        print(f">>> Updated passwords for {cursor.rowcount} users to '123'")
        
        # 2. Trim Whitespace
        cursor.execute("UPDATE Users_1 SET Username = LTRIM(RTRIM(Username)), Role = LTRIM(RTRIM(Role))")
        print(f">>> Trimmed whitespace for {cursor.rowcount} users")
        
        # 3. Check Services Table
        try:
            cursor.execute("SELECT COUNT(*) FROM Services")
            print(f">>> Services Table Exists. Count: {cursor.fetchone()[0]}")
        except:
            print(">>> Services Table MISSING! Creating it...")
            cursor.execute("""
                CREATE TABLE Services (
                    ServiceID INT IDENTITY(1,1) PRIMARY KEY,
                    ServiceName NVARCHAR(100) NOT NULL,
                    DefaultPrice DECIMAL(18, 2) DEFAULT 0
                )
            """)
            print(">>> Services Table Created.")

        conn.commit()
        
        # 4. List Users
        cursor.execute("SELECT UserID, Username, Role, Password FROM Users_1")
        users = cursor.fetchall()
        print("\n--- Current Users ---")
        for u in users:
            print(f"ID: {u[0]}, User: '{u[1]}', Role: '{u[2]}', Pass: '{u[3]}'")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    fix_users()
