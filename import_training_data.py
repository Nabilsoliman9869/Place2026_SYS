import pandas as pd
import pyodbc
import json
import os
from datetime import datetime

CONFIG_FILE = 'db_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection_string():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;Connect Timeout=60;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Connect Timeout=60;'

def clean_text(text):
    if pd.isna(text): return None
    return str(text).strip()

def clean_phone(phone):
    if pd.isna(phone): return None
    return str(phone).replace('.0', '').strip()

def import_training_data():
    print("🚀 Starting Phase 2 Import: Training Data...")
    file_path = 'GA2.1W34 - Yehia- 141225.xlsx'
    
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    try:
        conn = pyodbc.connect(get_db_connection_string())
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    # 1. Create Course & Batch
    print("\n--- 📚 Creating Course & Batch ---")
    course_name = "English Conversation"
    batch_name = "GA2.1W34 (Yehia)"
    
    # Check/Create Course
    cursor.execute("SELECT CourseID FROM Courses WHERE CourseName = ?", (course_name,))
    row = cursor.fetchone()
    if row:
        course_id = row[0]
    else:
        cursor.execute("INSERT INTO Courses (CourseName) VALUES (?)", (course_name,))
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        course_id = cursor.fetchone()[0]
        print(f"   ➕ Created Course: {course_name}")

    # Check/Create Batch
    cursor.execute("SELECT BatchID FROM CourseBatches WHERE BatchName = ?", (batch_name,))
    row = cursor.fetchone()
    if row:
        batch_id = row[0]
        print(f"   ✅ Batch exists: {batch_name}")
    else:
        cursor.execute("""
            INSERT INTO CourseBatches (CourseID, BatchName, Status, StartDate)
            VALUES (?, ?, 'Active', '2025-12-14')
        """, (course_id, batch_name))
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        batch_id = cursor.fetchone()[0]
        print(f"   ➕ Created Batch: {batch_name}")

    # 2. Import Students Manual List (From Chat)
    students_list = [
        {"name": "Aya Saied Reyad", "phone": "1100439565"},
        {"name": "Ahmed Abdelbast Mahmoued", "phone": "1276952697"},
        {"name": "Gerges Sabry Zakhir", "phone": "1277273902"},
        {"name": "Youssef Adam Youssef", "phone": "1123063095"},
        {"name": "Youssef Mahmoud Kamel", "phone": "1027669600"},
        {"name": "Ahmed Samy Mostafa", "phone": "1113801075"},
        {"name": "Ahmed Mohamed Naguib", "phone": "1113054176"},
        {"name": "Mohamed Abdelsalam Mostafa", "phone": "1145655000"},
        {"name": "yara fawzy", "phone": "1011729847"}
    ]
    
    print(f"📄 Processing {len(students_list)} manual entries...")
    count = 0

    for student in students_list:
        name = clean_text(student["name"])
        phone_str = clean_phone(student["phone"])
        
        # 3. Register Student (Candidate)
        cursor.execute("SELECT CandidateID FROM Candidates WHERE FullName = ? OR Phone = ?", (name, phone_str or 'N/A'))
        cand_row = cursor.fetchone()
        
        if cand_row:
            cand_id = cand_row[0]
            # print(f"   ✅ Student exists: {name}")
        else:
            # Create Candidate
            cursor.execute("INSERT INTO Candidates (FullName, Phone, Status, CreatedAt) VALUES (?, ?, 'Student', GETDATE())", 
                           (name, phone_str))
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            cand_id = cursor.fetchone()[0]
            print(f"   ➕ Created Student: {name}")

        # 4. Enroll in Batch
        cursor.execute("SELECT EnrollmentID FROM Enrollments WHERE BatchID = ? AND CandidateID = ?", (batch_id, cand_id))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO Enrollments (BatchID, CandidateID, Status, EnrollmentDate)
                VALUES (?, ?, 'Active', GETDATE())
            """, (batch_id, cand_id))
            conn.commit()
            count += 1
    
    print(f"\n✅ Enrolled {count} students into {batch_name}.")

    conn.close()

if __name__ == "__main__":
    import_training_data()
