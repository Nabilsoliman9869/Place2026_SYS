import pandas as pd
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

def clean_text(val):
    if pd.isna(val): return None
    return str(val).strip()

def import_data():
    print(">>> STARTING IMPORT...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Update Schema
    print(">>> UPDATING SCHEMA...")
    try:
        cursor.execute("ALTER TABLE Candidates ADD HRCode NVARCHAR(50)")
    except: pass
    try:
        cursor.execute("ALTER TABLE Candidates ADD NationalID NVARCHAR(50)")
    except: pass
    try:
        cursor.execute("ALTER TABLE Candidates ADD TargetLanguage NVARCHAR(50)")
    except: pass
    try:
        cursor.execute("ALTER TABLE Candidates ADD ProjectName NVARCHAR(100)")
    except: pass
    conn.commit()

    # 2. Read Excel
    print(">>> READING EXCEL...")
    xls = pd.ExcelFile('Exit Database (2).xlsx')
    df = pd.read_excel(xls, 'Data')

    # 3. Process Users (Trainers & Recruiters)
    print(">>> PROCESSING USERS...")
    trainers = df['Trainer'].dropna().unique()
    recruiters = df['Recruiter'].dropna().unique()

    # Trainers
    for t in trainers:
        t_name = clean_text(t)
        if not t_name: continue
        # Users_1
        username = t_name.split()[0].lower() + "_tr"
        cursor.execute("SELECT UserID FROM Users_1 WHERE FullName = ?", (t_name,))
        if not cursor.fetchone():
            print(f"Creating Trainer User: {t_name}")
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, '123', 'Trainer', ?)", (username, t_name))
        
        # Trainers Table
        cursor.execute("SELECT TrainerID FROM Trainers WHERE FullName = ?", (t_name,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Trainers (FullName, Specialization) VALUES (?, 'Language')", (t_name,))
    
    # Recruiters
    for r in recruiters:
        r_name = clean_text(r)
        if not r_name: continue
        username = r_name.split()[0].lower() + "_rec"
        
        # Check Username uniqueness explicitly to avoid integrity error
        cursor.execute("SELECT UserID FROM Users_1 WHERE Username = ?", (username,))
        if cursor.fetchone():
            # If username exists but FullName differs, append random digits
            import random
            username = f"{username}_{random.randint(10,99)}"
            
        cursor.execute("SELECT UserID FROM Users_1 WHERE FullName = ?", (r_name,))
        if not cursor.fetchone():
            print(f"Creating Recruiter User: {r_name} ({username})")
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, '123', 'Recruiter', ?)", (username, r_name))

    conn.commit()

    # 4. Process Batches (Waves)
    print(">>> PROCESSING BATCHES...")
    waves = df['TPA W#'].dropna().unique()
    
    # Ensure a default Course exists
    cursor.execute("SELECT CourseID FROM Courses WHERE CourseName='Legacy Import'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO Courses (CourseName, DefaultPrice) VALUES ('Legacy Import', 0)")
        conn.commit()
        cursor.execute("SELECT CourseID FROM Courses WHERE CourseName='Legacy Import'")
        course_id = cursor.fetchone()[0]
    else:
        course_id = row[0]

    # Ensure a default Room
    cursor.execute("SELECT RoomID FROM Classrooms WHERE RoomName='Virtual'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO Classrooms (RoomName, Capacity) VALUES ('Virtual', 999)")
        conn.commit()
        cursor.execute("SELECT RoomID FROM Classrooms WHERE RoomName='Virtual'")
        room_id = cursor.fetchone()[0]
    else:
        room_id = row[0]

    for w in waves:
        w_name = f"Wave {clean_text(w)}"
        cursor.execute("SELECT BatchID FROM CourseBatches WHERE BatchName = ?", (w_name,))
        if not cursor.fetchone():
            print(f"Creating Batch: {w_name}")
            # Try to link a trainer if ALL rows for this wave have same trainer
            trainer_for_wave = df[df['TPA W#'] == w]['Trainer'].mode()
            trainer_id = None
            if not trainer_for_wave.empty:
                t_name = clean_text(trainer_for_wave[0])
                cursor.execute("SELECT TrainerID FROM Trainers WHERE FullName=?", (t_name,))
                tr_row = cursor.fetchone()
                if tr_row: trainer_id = tr_row[0]
            
            cursor.execute("INSERT INTO CourseBatches (BatchName, CourseID, TrainerID, RoomID, Status) VALUES (?, ?, ?, ?, 'Completed')", 
                           (w_name, course_id, trainer_id, room_id))
    conn.commit()

    # 5. Process Candidates
    print(">>> PROCESSING CANDIDATES...")
    count = 0
    for index, row in df.iterrows():
        try:
            full_name = clean_text(row.get('Full Name'))
            if not full_name: continue
            
            phone = clean_text(row.get('Contact Number'))
            hr_id = clean_text(row.get('HRID'))
            national_id = clean_text(row.get('ID Number'))
            grad_status = clean_text(row.get('Graduation Status'))
            language = clean_text(row.get('Language'))
            project = clean_text(row.get('Project'))
            recruiter_name = clean_text(row.get('Recruiter'))
            wave_val = clean_text(row.get('TPA W#'))
            hired_val = clean_text(row.get('Hired?'))
            
            # Determine Status
            status = 'Imported'
            if hired_val and 'yes' in hired_val.lower():
                status = 'Hired'
            
            # Find SalesAgentID
            sales_agent_id = None
            if recruiter_name:
                cursor.execute("SELECT UserID FROM Users_1 WHERE FullName=?", (recruiter_name,))
                u_row = cursor.fetchone()
                if u_row: sales_agent_id = u_row[0]
            
            # Insert Candidate
            cursor.execute("""
                INSERT INTO Candidates (FullName, Phone, HRCode, NationalID, GraduationStatus, TargetLanguage, ProjectName, SalesAgentID, Status, InterestLevel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'High')
            """, (full_name, phone, hr_id, national_id, grad_status, language, project, sales_agent_id, status))
            
            # Get CandidateID (Assuming IDENTITY)
            cursor.execute("SELECT @@IDENTITY")
            candidate_id = cursor.fetchone()[0]
            
            # Enroll in Batch
            if wave_val:
                w_name = f"Wave {wave_val}"
                cursor.execute("SELECT BatchID FROM CourseBatches WHERE BatchName=?", (w_name,))
                b_row = cursor.fetchone()
                if b_row:
                    batch_id = b_row[0]
                    cursor.execute("INSERT INTO Enrollments (CandidateID, BatchID, Status) VALUES (?, ?, 'Completed')", (candidate_id, batch_id))
            
            count += 1
            if count % 50 == 0: print(f"Imported {count} candidates...")
            
        except Exception as e:
            print(f"Error Row {index}: {e}")

    conn.commit()
    print(f">>> IMPORT COMPLETE. Total Candidates: {count}")

if __name__ == "__main__":
    import_data()
