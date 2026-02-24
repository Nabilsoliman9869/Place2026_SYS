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

def extreme_force_delete():
    conn = get_db_connection()
    cursor = conn.cursor()
    print(">>> EXTREME FORCE DELETING 'aaa' <<<")
    
    # Target: 'aaa' which matches 'RoaaAlhussien Ahmed Hassan' partially in previous run?
    # Wait, the previous log said: "aaa" found 2 matches.
    # One was deleted? Or failed?
    # The error message said: FK__Matches__Candida__...
    # So we need to target 'aaa' again.
    
    targets = ['aaa']
    
    for name in targets:
        cursor.execute("SELECT CandidateID, FullName FROM Candidates WHERE FullName LIKE ?", (f"%{name}%",))
        matches = cursor.fetchall()
        
        for cid, fullname in matches:
            try:
                print(f"Targeting: {fullname} (ID {cid})")
                
                # 1. Delete Matches
                cursor.execute("DELETE FROM Matches WHERE CandidateID=?", (cid,))
                print(" - Deleted Matches")
                
                # 2. Delete TASchedules
                cursor.execute("DELETE FROM TASchedules WHERE CandidateID=?", (cid,))
                print(" - Deleted TASchedules")
                
                # 3. Delete Candidate
                cursor.execute("DELETE FROM Candidates WHERE CandidateID=?", (cid,))
                print(" - Deleted Candidate")
                
            except Exception as e:
                print(f"   [ERROR] {e}")

    conn.commit()
    print(">>> DONE <<<")

if __name__ == "__main__":
    extreme_force_delete()
