import pandas as pd
import pyodbc
import json
import os
import sys
import random

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

def clean_text(val):
    if pd.isna(val): return None
    s = str(val).strip()
    return s if s.lower() != 'nan' and s != '' else None

def import_booking():
    print(">>> STARTING BOOKING IMPORT...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Read Excel
    print(">>> READING EXCEL...")
    df = pd.read_excel('Booking sheet.xlsx')

    # 2. Process Recruiters First
    print(">>> PROCESSING RECRUITERS...")
    recruiters = df['Recruiter'].dropna().unique()
    
    for r in recruiters:
        r_name = clean_text(r)
        if not r_name: continue
        
        # Check if user exists by FullName
        cursor.execute("SELECT UserID FROM Users_1 WHERE FullName = ?", (r_name,))
        if not cursor.fetchone():
            # Generate Unique Username
            base_username = r_name.split()[0].lower() + "_rec"
            username = base_username
            
            # Check username uniqueness
            while True:
                cursor.execute("SELECT UserID FROM Users_1 WHERE Username = ?", (username,))
                if not cursor.fetchone(): break
                username = f"{base_username}_{random.randint(10,99)}"
            
            print(f"Creating Recruiter: {r_name} ({username})")
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, '123', 'Recruiter', ?)", (username, r_name))
    
    conn.commit()

    # 3. Process Candidates
    print(">>> PROCESSING CANDIDATES...")
    count = 0
    updated = 0
    
    for index, row in df.iterrows():
        try:
            full_name = clean_text(row.get('Full Name'))
            if not full_name: continue
            
            phone = clean_text(row.get('Mobile Number'))
            national_id = clean_text(row.get('National ID'))
            english_level = clean_text(row.get('English Level'))
            status_val = clean_text(row.get('Status'))
            recruiter_name = clean_text(row.get('Recruiter'))
            date_val = row.get('Date') # Might need formatting
            system_val = clean_text(row.get('System'))
            
            # Map Status
            status = 'New'
            if status_val:
                if 'hired' in status_val.lower(): status = 'Hired'
                elif 'pending' in status_val.lower(): status = 'Pending'
                elif 'rejected' in status_val.lower(): status = 'Rejected'
                else: status = 'Imported' # Default for unknown statuses
            
            # Find SalesAgentID
            sales_agent_id = None
            if recruiter_name:
                cursor.execute("SELECT UserID FROM Users_1 WHERE FullName=?", (recruiter_name,))
                u_row = cursor.fetchone()
                if u_row: sales_agent_id = u_row[0]

            # Check duplication by NationalID or Phone
            candidate_id = None
            if national_id:
                cursor.execute("SELECT CandidateID FROM Candidates WHERE NationalID=?", (national_id,))
                c_row = cursor.fetchone()
                if c_row: candidate_id = c_row[0]
            
            if not candidate_id and phone:
                cursor.execute("SELECT CandidateID FROM Candidates WHERE Phone=?", (phone,))
                c_row = cursor.fetchone()
                if c_row: candidate_id = c_row[0]
                
            if candidate_id:
                # Update existing
                cursor.execute("""
                    UPDATE Candidates 
                    SET EnglishLevel=?, Status=?, SalesAgentID=?, SourceChannel=?
                    WHERE CandidateID=?
                """, (english_level, status, sales_agent_id, 'BookingSheet', candidate_id))
                updated += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO Candidates (FullName, Phone, NationalID, EnglishLevel, Status, SalesAgentID, SourceChannel, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, 'BookingSheet', ?)
                """, (full_name, phone, national_id, english_level, status, sales_agent_id, date_val if date_val else None))
                count += 1
                
            if (count + updated) % 50 == 0: print(f"Processed {count + updated} rows...")
            
        except Exception as e:
            print(f"Error Row {index}: {e}")

    conn.commit()
    print(f">>> IMPORT COMPLETE. New: {count}, Updated: {updated}")

    # 4. Generate User List
    print("\n>>> GENERATING USER LIST...")
    cursor.execute("SELECT FullName, Username, Role, Password FROM Users_1 ORDER BY Role, Username")
    users = cursor.fetchall()
    
    print(f"{'FullName':<30} | {'Username':<20} | {'Role':<15} | {'Password'}")
    print("-" * 80)
    for u in users:
        fname = u[0] if u[0] else "N/A"
        uname = u[1] if u[1] else "N/A"
        role = u[2] if u[2] else "N/A"
        pwd = u[3] if u[3] else "N/A"
        print(f"{fname:<30} | {uname:<20} | {role:<15} | {pwd}")

if __name__ == "__main__":
    import_booking()
