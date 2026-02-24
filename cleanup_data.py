import pyodbc
import json
import os
import sys
import re

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

def clean_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- CLEANING CANDIDATES ---")
    
    # 1. Remove Garbage (N/A names, too short, test)
    print("Identifying invalid candidates...")
    cursor.execute("SELECT CandidateID, FullName FROM Candidates")
    all_cands = cursor.fetchall()
    
    to_delete = []
    for cid, name in all_cands:
        name_str = str(name).strip().lower()
        if not name or name_str in ['n/a', 'nan', 'none', 'test', 'unknown'] or len(name_str) < 3:
            to_delete.append(cid)
            
    print(f"Found {len(to_delete)} invalid candidates (N/A, empty, test).")
    
    if to_delete:
        # Batch delete
        placeholders = ','.join('?' * len(to_delete))
        cursor.execute(f"DELETE FROM Candidates WHERE CandidateID IN ({placeholders})", to_delete)
        conn.commit()
        print("Deleted invalid candidates.")
    
    # 2. Sort/Reorder is a UI thing, DB doesn't care. But we can ensure NULLs are handled.
    # We will output a report of remaining count.
    cursor.execute("SELECT COUNT(*) FROM Candidates")
    print(f"Remaining Valid Candidates: {cursor.fetchone()[0]}")

def clean_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- CLEANING RECRUITERS (DUPLICATES) ---")
    
    # Fetch all Recruiters
    cursor.execute("SELECT UserID, Username, FullName FROM Users_1 WHERE Role='Recruiter' ORDER BY Username")
    users = cursor.fetchall()
    
    # Simple Deduplication Logic:
    # Group by "Similiar Name". 
    # Example: "abdelrahman_rec", "abdelrahman_rec_24" -> Base: "abdelrahman"
    
    seen_bases = {}
    duplicates = []
    
    for uid, uname, fname in users:
        # Extract base name (remove digits and common suffixes like _rec)
        base = uname.lower().replace('_rec', '').replace('.', '')
        base = re.sub(r'\d+', '', base).strip()
        
        if base in seen_bases:
            duplicates.append((uid, uname, seen_bases[base])) # (CurrentID, CurrentName, KeptName)
        else:
            seen_bases[base] = uname # Keep the first one encountered (usually the cleanest if sorted)
            
    print(f"Found {len(duplicates)} potential duplicate recruiters.")
    for uid, bad_name, kept_name in duplicates:
        print(f" - Delete: {bad_name} (Duplicate of {kept_name})")
        
        # Action: Delete
        # NOTE: In production, we should reassign their data (Candidates) to the 'kept' user.
        # Let's do that safely.
        
        # Find Kept User ID
        cursor.execute("SELECT UserID FROM Users_1 WHERE Username=?", (kept_name,))
        kept_id = cursor.fetchone()
        if kept_id:
            kept_id = kept_id[0]
            # Reassign Candidates
            cursor.execute("UPDATE Candidates SET SalesAgentID=? WHERE SalesAgentID=?", (kept_id, uid))
            # Delete User
            cursor.execute("DELETE FROM Users_1 WHERE UserID=?", (uid,))
            conn.commit()
            print(f"   -> Data reassigned to {kept_name}, User deleted.")

    print("Duplicate cleanup complete.")

if __name__ == "__main__":
    clean_candidates()
    clean_users()
