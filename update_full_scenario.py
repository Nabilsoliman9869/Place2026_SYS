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

def update_full_scenario():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Starting Full Scenario Update...")

        # 1. Update Candidates Table (Sourcing & Tracking)
        print(">>> Updating Candidates Schema...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Candidates' AND COLUMN_NAME='SourceChannel')
            BEGIN
                ALTER TABLE Candidates ADD SourceChannel NVARCHAR(100); -- Facebook, Referral, etc.
                ALTER TABLE Candidates ADD SecondaryPhone NVARCHAR(50);
                ALTER TABLE Candidates ADD RecruiterID INT; -- Linked to Users (Who owns this lead)
                ALTER TABLE Candidates ADD GraduationStatus NVARCHAR(50); -- Graduated, Student
                ALTER TABLE Candidates ADD Rejoiner BIT DEFAULT 0; -- Is he rejoining?
                ALTER TABLE Candidates ADD Nationality NVARCHAR(50);
                ALTER TABLE Candidates ADD Location NVARCHAR(100);
            END
        """)

        # 2. Add Job Vacancies (Detailed)
        print(">>> Creating JobVacancies Table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='JobVacancies' AND xtype='U')
            CREATE TABLE JobVacancies (
                VacancyID INT IDENTITY(1,1) PRIMARY KEY,
                ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
                RoleTitle NVARCHAR(100),
                Shifts NVARCHAR(200), -- Rotational, Night, etc.
                Location NVARCHAR(100),
                SalaryPackage NVARCHAR(100), -- 20.5K, etc.
                Transportation NVARCHAR(50), -- Provided / Not
                Insurance NVARCHAR(50), -- Social & Medical
                GenderPreference NVARCHAR(50) DEFAULT 'Any',
                MaxAge INT,
                Status NVARCHAR(50) DEFAULT 'Open',
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)

        # 3. Add Screening & Submissions (The Pipeline)
        print(">>> Creating Pipeline Tables...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PipelineStages' AND xtype='U')
            CREATE TABLE PipelineStages (
                StageID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                VacancyID INT FOREIGN KEY REFERENCES JobVacancies(VacancyID),
                
                -- Stage 1: Screening
                ScreeningStatus NVARCHAR(50) DEFAULT 'Pending', -- Pass, Fail
                ScreeningNotes NVARCHAR(MAX),
                
                -- Stage 2: TA Assessment (Recruitment Specific)
                TAStatus NVARCHAR(50) DEFAULT 'Pending',
                TAScore_CEFR NVARCHAR(10),
                TA_Recommendation NVARCHAR(MAX),
                
                -- Stage 3: Client Submission
                SubmissionStatus NVARCHAR(50) DEFAULT 'Not Submitted', -- Submitted, Shortlisted, Rejected, Accepted
                SubmissionDate DATETIME,
                
                -- Stage 4: Validation (30 Days)
                ValidationStartDate DATE,
                ValidationEndDate DATE,
                ValidationOutcome NVARCHAR(50), -- Passed, Failed
                
                UpdatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        
        # 4. Add Roles for Breakdown (AM, Recruiter, Allocator)
        # We will reuse Users_1 table, just ensure roles are understood in code.

        conn.commit()
        print(">>> Database Updated Successfully for Full Workflow.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    update_full_scenario()
