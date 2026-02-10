import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def update_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    # Define users to create/update
    # Format: (Username, Role, FullName)
    users_to_update = [
        ('habiba', 'Recruiter', 'Habiba (Recruiter)'),
        ('menna', 'Talent', 'Menna (Talent)'),
        ('zeyed', 'Allocator', 'Zeyed (Allocator)'),
        ('aya', 'AllocationManager', 'Aya (Allocation Manager)'),
        ('ahmed_adel', 'AllocationSpecialist', 'Ahmed Adel (Allocation Specialist)')
    ]
    
    print(f"{'Username':<20} {'Role':<25} {'Action':<15}")
    print("-" * 60)
    
    for username, role, fullname in users_to_update:
        # Check if user exists
        cursor.execute("SELECT UserID FROM Users_1 WHERE Username=?", (username,))
        row = cursor.fetchone()
        
        if row:
            # Update existing
            cursor.execute("UPDATE Users_1 SET Role=?, Password='123', FullName=? WHERE Username=?", 
                           (role, fullname, username))
            action = "UPDATED"
        else:
            # Create new
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, '123', ?, ?)", 
                           (username, role, fullname))
            action = "CREATED"
            
        print(f"{username:<20} {role:<25} {action:<15}")

    conn.commit()
    conn.close()
    print("-" * 60)
    print("All users processed successfully.")

if __name__ == '__main__':
    update_users()
