import pyodbc
import json
import os
import sys
import re
from datetime import datetime

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

def is_date(string):
    """Check if string looks like a date/timestamp"""
    if not string: return False
    # Common date patterns in Excel imports: 2024-01-01, 01/01/2024, 2024-01-01 00:00:00
    # Regex for YYYY-MM-DD or DD/MM/YYYY or YYYY-MM-DD HH:MM:SS
    if re.match(r'\d{4}-\d{2}-\d{2}', str(string)): return True
    if re.match(r'\d{2}/\d{2}/\d{4}', str(string)): return True
    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(string)): return True
    return False

def clean_candidates_deep():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- DEEP CLEANING CANDIDATES ---")
    
    cursor.execute("SELECT CandidateID, FullName, Phone FROM Candidates")
    all_cands = cursor.fetchall()
    
    to_delete = []
    reasons = {} # ID -> Reason
    
    for cid, name, phone in all_cands:
        name_str = str(name).strip()
        
        # Rule 1: Name looks like a Date/Time
        if is_date(name_str):
            to_delete.append(cid)
            reasons[cid] = f"Name is Date: {name_str}"
            continue
            
        # Rule 2: Name is too short or just numbers
        if len(name_str) < 3 or name_str.isdigit():
            to_delete.append(cid)
            reasons[cid] = f"Name Invalid: {name_str}"
            continue
            
        # Rule 3: Missing Phone (Completeness)
        if not phone or len(str(phone).strip()) < 5:
            to_delete.append(cid)
            reasons[cid] = f"Missing Phone: {phone}"
            continue

    # Filter out candidates with dependencies (Enrollments, Invoices, Matches)
    print(f"Initial Invalid Rows: {len(to_delete)}")
    
    if to_delete:
        final_delete = []
        for cid in to_delete:
            # Check Enrollments
            cursor.execute("SELECT COUNT(*) FROM Enrollments WHERE CandidateID=?", (cid,))
            if cursor.fetchone()[0] > 0:
                print(f"Skipping ID {cid} (Has Enrollments)")
                continue
                
            # Check Invoices
            cursor.execute("SELECT COUNT(*) FROM InvoiceHeaders WHERE CandidateID=?", (cid,))
            if cursor.fetchone()[0] > 0:
                 print(f"Skipping ID {cid} (Has Invoices)")
                 continue

            # Check Matches
            cursor.execute("SELECT COUNT(*) FROM Matches WHERE CandidateID=?", (cid,))
            if cursor.fetchone()[0] > 0:
                 print(f"Skipping ID {cid} (Has Matches)")
                 continue
                 
            final_delete.append(cid)
            
        to_delete = final_delete
    
    print(f"Final Deletable Rows: {len(to_delete)}")
    
    if to_delete:
        print("Deleting... (Sample Reasons)")
        # Show first 5 reasons
        for i, cid in enumerate(to_delete[:5]):
            print(f" - ID {cid}: {reasons[cid]}")
            
        # Batch delete
        # SQL Server limit for parameters is ~2100. Chunk it.
        chunk_size = 1000
        for i in range(0, len(to_delete), chunk_size):
            chunk = to_delete[i:i+chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f"DELETE FROM Candidates WHERE CandidateID IN ({placeholders})", chunk)
            conn.commit()
            
        print("Deep cleanup complete.")
    else:
        print("No invalid rows found.")

if __name__ == "__main__":
    clean_candidates_deep()
