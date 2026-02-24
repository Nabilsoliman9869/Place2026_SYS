import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def verify_workflow_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    roles = {
        'Recruiter': 'adl_rec',
        'Talent': 'mennatalla',
        'Allocator': 'allocator1',
        'AllocationSpecialist': 'alloc_sp',
        'AccountManager': 'acc_mgr'
    }
    
    print(f"{'Role':<25} {'Target User':<20} {'Status':<15} {'Password'}")
    print("-" * 70)
    
    for role, target_user in roles.items():
        cursor.execute("SELECT UserID, Username, Password FROM Users_1 WHERE Username=?", (target_user,))
        row = cursor.fetchone()
        
        if row:
            status = "EXISTS"
            pwd = row.Password
        else:
            status = "MISSING"
            pwd = "N/A"
            # Auto-create if missing
            try:
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, ?, ?, ?)", 
                               (target_user, '123', role, f"{target_user} ({role})"))
                conn.commit()
                status = "CREATED"
                pwd = '123'
            except:
                status = "ERROR"
        
        print(f"{role:<25} {target_user:<20} {status:<15} {pwd}")

    conn.close()

if __name__ == '__main__':
    verify_workflow_users()
