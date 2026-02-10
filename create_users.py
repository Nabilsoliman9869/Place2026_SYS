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

def create_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    users = [
        ('marketing1', '123', 'Marketing'),
        ('sales1', '123', 'Sales'),
        ('sales2', '123', 'Sales'),
        ('ta_rec', '123', 'Talent_Recruitment'),
        ('ta_train', '123', 'Talent_Training'),
        ('recruiter1', '123', 'Recruitment'),
        ('allocator1', '123', 'Allocator'),
        ('am1', '123', 'AccountManager'),
        ('train_mgr', '123', 'TrainingManager'),
        ('trainer1', '123', 'Trainer'),
        ('admin', '123', 'Manager')
    ]
    
    print(">>> Creating Users...")
    for u in users:
        try:
            # Check if exists
            cursor.execute("SELECT Count(*) FROM Users_1 WHERE Username=?", (u[0],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role) VALUES (?, ?, ?)", u)
                print(f"Created: {u[0]} ({u[2]})")
            else:
                print(f"Exists: {u[0]}")
        except Exception as e:
            print(f"Error creating {u[0]}: {e}")
            
    conn.commit()
    print(">>> Done.")

if __name__ == '__main__':
    create_users()
