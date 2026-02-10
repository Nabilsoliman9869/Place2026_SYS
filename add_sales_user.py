import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def add_sales_user():
    if not os.path.exists(CONFIG_FILE): return
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if exists first
        cursor.execute("SELECT UserID FROM Users WHERE Username = 'sales'")
        if not cursor.fetchone():
            print("Adding sales user...")
            # Using your existing columns (assuming ID, Username, Password, Role)
            # If FullName doesn't exist in your schema yet, we skip it or add it if you allowed the previous fix.
            # I will try the standard insert first based on your description: manager, 1, Manager, manager123
            
            try:
                # Try simple insert compatible with your described schema
                cursor.execute("INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)", 
                               ('sales', 'sales123', 'Sales'))
            except:
                # Fallback if FullName is required/exists
                cursor.execute("INSERT INTO Users (Username, Password, Role, FullName) VALUES (?, ?, ?, ?)", 
                               ('sales', 'sales123', 'Sales', 'Sales Representative'))
                
            conn.commit()
            print("Sales user added successfully: User=sales, Pass=sales123")
        else:
            print("Sales user already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error adding user: {e}")

if __name__ == '__main__':
    add_sales_user()
