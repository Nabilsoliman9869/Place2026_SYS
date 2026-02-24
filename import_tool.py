import pandas as pd
import pyodbc
import json
import os
import sys

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

def import_candidates(file_path):
    print(f">>> Importing: {file_path}")
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Map Excel Columns to DB Columns
        # e, Interval, Recruiter, Source, Company, Candidate Name, PriNumber, Sec Number, Email, ...
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                full_name = str(row.get('Candidate Name', '')).strip()
                if not full_name or full_name == 'nan': continue
                
                phone = str(row.get('PriNumber', '')).strip()
                sec_phone = str(row.get('Sec Number', '')).strip()
                email = str(row.get('Email', '')).strip()
                source = str(row.get('Source', '')).strip()
                recruiter_name = str(row.get('Recruiter', '')).strip()
                nationality = str(row.get('Nationality', '')).strip()
                location = str(row.get('Location', '')).strip()
                
                # Check duplication
                cursor.execute("SELECT Count(*) FROM Candidates WHERE Phone=?", (phone,))
                if cursor.fetchone()[0] > 0:
                    print(f"Skipping Duplicate: {full_name} ({phone})")
                    continue
                
                # Resolve Recruiter ID if possible (Optional)
                recruiter_id = None
                if recruiter_name:
                    cursor.execute("SELECT UserID FROM Users_1 WHERE Username=?", (recruiter_name,))
                    res = cursor.fetchone()
                    if res: recruiter_id = res[0]
                
                cursor.execute("""
                    INSERT INTO Candidates (FullName, Phone, SecondaryPhone, Email, SourceChannel, RecruiterID, Nationality, Location, Status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Imported')
                """, (full_name, phone, sec_phone, email, source, recruiter_id, nationality, location))
                
                success_count += 1
                
            except Exception as e:
                print(f"Error Row {index}: {e}")
                error_count += 1
                
        conn.commit()
        print(f">>> Import Completed. Success: {success_count}, Errors: {error_count}")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == '__main__':
    # File path passed as argument or hardcoded for testing
    if len(sys.argv) > 1:
        import_candidates(sys.argv[1])
    else:
        print("Usage: python import_tool.py <file_path>")
