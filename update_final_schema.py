import pyodbc
import json
import os

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

def update_final_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Starting Final Schema Update (Recruitment & Training Plans)...")

        # 1. TrainingPlans Table (Head of Training sets this)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainingPlans' AND xtype='U')
            CREATE TABLE TrainingPlans (
                PlanID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT FOREIGN KEY REFERENCES Enrollments(EnrollmentID),
                WeekNumber INT NOT NULL,
                FocusArea NVARCHAR(200), -- e.g. "Pronunciation & Basic Grammar"
                TargetGoals NVARCHAR(MAX), -- Specific goals for this week
                CreatedBy INT, -- Head of Training ID
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print(">>> TrainingPlans Table Created.")

        # 2. ClientInterviews Table (Recruitment Feedback)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientInterviews' AND xtype='U')
            CREATE TABLE ClientInterviews (
                InterviewID INT IDENTITY(1,1) PRIMARY KEY,
                MatchID INT FOREIGN KEY REFERENCES Matches(MatchID),
                InterviewDate DATETIME DEFAULT GETDATE(),
                Status NVARCHAR(50), -- 'Accepted', 'Rejected', 'Pending'
                Feedback NVARCHAR(MAX), -- Why rejected/accepted?
                RejectionReason NVARCHAR(100), -- Dropdown: "Weak English", "Attitude", "Technical Skills", "Salary"
                ActionRequired NVARCHAR(200), -- "Retrain English", "Blacklist", "None"
                RecordedBy INT
            )
        """)
        print(">>> ClientInterviews Table Created.")
        
        # 3. Add 'Head of Training' Role if not handled by code (we'll handle roles in app logic)
        
        # 4. Add 'HeadTrainerID' to Waves/Batches to assign responsibility
        try:
            cursor.execute("ALTER TABLE CourseBatches ADD HeadTrainerID INT")
            print(">>> Added HeadTrainerID to CourseBatches.")
        except: pass

        # 5. Ensure Attendance table supports 'Batch Mode' (it already does via EnrollmentID, logic is in UI)

        conn.commit()
        print(">>> Final Schema Update Completed.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    update_final_schema()
