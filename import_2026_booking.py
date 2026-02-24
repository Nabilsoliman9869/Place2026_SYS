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

def import_booking_2026():
    print(">>> STARTING 2026 BOOKING IMPORT...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Read Excel
    print(">>> READING EXCEL (2026 booking.xlsx)...")
    try:
        # Read first few rows to find header
        df_raw = pd.read_excel('2026 booking.xlsx', header=None, nrows=20)
        
        # Find row with "Name" or "Full Name"
        header_row_idx = 0
        for i, row in df_raw.iterrows():
            row_str = row.astype(str).str.lower().tolist()
            if any('name' in s for s in row_str) and any('mobile' in s or 'phone' in s or 'number' in s for s in row_str):
                header_row_idx = i
                break
        
        print(f"Detected Header Row Index: {header_row_idx}")
        
        # Re-read with correct header
        df = pd.read_excel('2026 booking.xlsx', header=header_row_idx)
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. Process Recruiters First
    print(">>> PROCESSING RECRUITERS...")
    # Find Recruiter column dynamically
    rec_col = next((c for c in df.columns if 'recruiter' in str(c).lower()), None)
    
    if rec_col:
        recruiters = df[rec_col].dropna().unique()
        
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
    else:
        print("Warning: 'Recruiter' column not found.")

    # 3. Process Candidates
    print(">>> PROCESSING CANDIDATES...")
    count = 0
    updated = 0
    
    # Identify Columns (Flexible matching)
    # The columns from check are: ['Unnamed: 0', 'Interviewer', 'Status', 'Recruiter', 'Source', 'Company', 'Name', 'Number', 'Sec Number', 'Email', 'Grad Status', 'CEFR', 'Military Status', 'Age', 'Location', 'RTS/ Date', 'Flex with shifts', 'Comments']
    # 'Name' column is literally 'Name'. 'Number' is phone.
    
    col_map = {
        'name': next((c for c in df.columns if str(c).strip() == 'Name'), None),
        'phone': next((c for c in df.columns if 'Number' == str(c).strip() or 'Mobile' in str(c)), None),
        'national_id': next((c for c in df.columns if 'national' in str(c).lower() or 'id' in str(c).lower()), None),
        'english': next((c for c in df.columns if 'CEFR' in str(c) or 'english' in str(c).lower()), None),
        'status': next((c for c in df.columns if 'status' in str(c).lower() and 'grad' not in str(c).lower()), None),
        'recruiter': next((c for c in df.columns if 'recruiter' in str(c).lower()), None),
        'date': next((c for c in df.columns if 'date' in str(c).lower()), None),
        'system': next((c for c in df.columns if 'system' in str(c).lower() or 'source' in str(c).lower()), None)
    }
    
    print(f"Column Mapping: {col_map}")

    for index, row in df.iterrows():
        try:
            full_name = clean_text(row.get(col_map['name'])) if col_map['name'] else None
            if not full_name: continue
            
            phone = clean_text(row.get(col_map['phone'])) if col_map['phone'] else None
            national_id = clean_text(row.get(col_map['national_id'])) if col_map['national_id'] else None
            english_level = clean_text(row.get(col_map['english'])) if col_map['english'] else None
            status_val = clean_text(row.get(col_map['status'])) if col_map['status'] else None
            recruiter_name = clean_text(row.get(col_map['recruiter'])) if col_map['recruiter'] else None
            date_val = row.get(col_map['date']) if col_map['date'] else None
            
            # Map Status
            status = 'New'
            if status_val:
                if 'hired' in status_val.lower(): status = 'Hired'
                elif 'pending' in status_val.lower(): status = 'Pending'
                elif 'rejected' in status_val.lower(): status = 'Rejected'
                else: status = 'Imported'
            
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
            
            # Validate Date (Parameter 10 in error logs refers to Date)
            # Ensure it is a valid date or None
            import datetime
            if date_val:
                try:
                    # Try converting to datetime if it's a string, or ensure it's a valid object
                    if isinstance(date_val, str):
                        # Try parsing common formats or ignore
                        pass # Let SQL Driver handle or set to None if fails
                    elif isinstance(date_val, (int, float)):
                         # Excel serial date? convert or ignore
                         date_val = None
                except:
                    date_val = None
            else:
                date_val = None

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
                """, (english_level, status, sales_agent_id, '2026Booking', candidate_id))
                updated += 1
            else:
                # Insert new
                # FIX: Explicitly handle Date parameter to avoid RPC/TDS error with None/Invalid types
                # Using parameters properly
                cursor.execute("""
                    INSERT INTO Candidates (FullName, Phone, NationalID, EnglishLevel, Status, SalesAgentID, SourceChannel, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, '2026Booking', ?)
                """, (full_name, phone, national_id, english_level, status, sales_agent_id, date_val))
                count += 1
                
            if (count + updated) % 50 == 0: print(f"Processed {count + updated} rows...")
            
        except Exception as e:
            print(f"Error Row {index}: {e}")

    conn.commit()
    print(f">>> IMPORT COMPLETE. New: {count}, Updated: {updated}")

if __name__ == "__main__":
    import_booking_2026()
