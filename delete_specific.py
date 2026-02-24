import pyodbc
import json
import os
import sys

# --- CONFIG ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(application_path, 'db_config.json')

def get_db_connection():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def delete_targets():
    conn = get_db_connection()
    cursor = conn.cursor()
    print(">>> DELETING SPECIFIC TARGETS <<<")
    
    targets = [
        'Nadine Nabil', 'Test 3', 'ررر', 'ليىبيايا', 
        'seif ayman', 'aaa', 'عمر نبيل', 'ssssssss', 'asasasa'
    ]
    
    total_deleted = 0
    
    for name in targets:
        # Find ID first
        cursor.execute("SELECT CandidateID, FullName FROM Candidates WHERE FullName LIKE ?", (f"%{name}%",))
        matches = cursor.fetchall()
        
        if not matches:
            print(f" - '{name}': No match found.")
            continue
            
        print(f" - '{name}': Found {len(matches)} matches.")
        
        for cid, fullname in matches:
            # Check Dependencies
            try:
                # Enrollments
                cursor.execute("SELECT COUNT(*) FROM Enrollments WHERE CandidateID=?", (cid,))
                if cursor.fetchone()[0] > 0:
                    print(f"   [SKIP] {fullname} (ID {cid}) has Enrollments.")
                    continue
                    
                # Invoices
                cursor.execute("SELECT COUNT(*) FROM InvoiceHeaders WHERE CandidateID=?", (cid,))
                if cursor.fetchone()[0] > 0:
                    print(f"   [SKIP] {fullname} (ID {cid}) has Invoices.")
                    continue

                # Matches
                cursor.execute("SELECT COUNT(*) FROM Matches WHERE CandidateID=?", (cid,))
                if cursor.fetchone()[0] > 0:
                    print(f"   [SKIP] {fullname} (ID {cid}) has Matches.")
                    continue
                
                # Safe to Delete
                cursor.execute("DELETE FROM Candidates WHERE CandidateID=?", (cid,))
                print(f"   [DELETED] {fullname} (ID {cid})")
                total_deleted += 1
                
            except Exception as e:
                print(f"   [ERROR] Could not delete {fullname}: {e}")

    conn.commit()
    print(f"\n>>> DONE. Total Deleted: {total_deleted} <<<")

if __name__ == "__main__":
    delete_targets()
