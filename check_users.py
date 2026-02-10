import pyodbc
import json

CONFIG_FILE = 'db_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection_string():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;Connect Timeout=60;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};Connect Timeout=60;'

def get_users_by_role(role):
    conn = pyodbc.connect(get_db_connection_string())
    cursor = conn.cursor()
    cursor.execute("SELECT Username, FullName FROM Users_1 WHERE Role = ?", (role,))
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_training_users():
    print("\n--- 🎓 Training Department Users ---")
    
    # Training Manager
    print("\n🔹 Training Managers:")
    managers = get_users_by_role('Training Manager')
    for u in managers: print(f"   - User: {u[0]} (Name: {u[1]})")
    if not managers: print("   (No users found)")

    # Trainer
    print("\n🔹 Trainers:")
    trainers = get_users_by_role('Trainer')
    for u in trainers: print(f"   - User: {u[0]} (Name: {u[1]})")
    if not trainers: print("   (No users found)")
    
    # Specific Check for 'Rana'
    conn = pyodbc.connect(get_db_connection_string())
    cursor = conn.cursor()
    cursor.execute("SELECT Username, Role FROM Users_1 WHERE FullName LIKE '%Rana%' OR Username LIKE '%Rana%'")
    ranas = cursor.fetchall()
    print("\n🔹 Search for 'Rana':")
    for r in ranas: print(f"   - User: {r[0]} (Role: {r[1]})")
    conn.close()

    # Create Users if missing
    conn = pyodbc.connect(get_db_connection_string())
    cursor = conn.cursor()
    
    # 1. Rana (Training Manager)
    cursor.execute("SELECT UserID FROM Users_1 WHERE Username = 'rana'")
    if not cursor.fetchone():
        print("\n➕ Creating User: Rana (Training Manager)...")
        cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES ('rana', '123456', 'Training Manager', 'Rana Training')")
        conn.commit()
    else:
        print("\n✅ User 'rana' exists.")

    # 2. Yehia (Trainer)
    cursor.execute("SELECT UserID FROM Users_1 WHERE Username = 'yehia'")
    if not cursor.fetchone():
        print("\n➕ Creating User: Yehia (Trainer)...")
        cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES ('yehia', '123456', 'Trainer', 'Yehia Trainer')")
        conn.commit()
    else:
        print("\n✅ User 'yehia' exists.")
        
    conn.close()

if __name__ == "__main__":
    get_all_training_users()
