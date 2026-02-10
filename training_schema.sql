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

def update_training_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Starting Training Schema Update...")

        # 1. Update Candidates Table (Intent & Engagement)
        print(">>> Updating Candidates Schema...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Candidates' AND COLUMN_NAME='PrimaryIntent')
            BEGIN
                ALTER TABLE Candidates ADD PrimaryIntent NVARCHAR(50); -- Training, Career, Both
                ALTER TABLE Candidates ADD EngagementStatus NVARCHAR(50); -- Engaged, Not Engaged
                ALTER TABLE Candidates ADD AvailabilityConstraints NVARCHAR(MAX);
            END
        """)

        # 2. Placement Tests Table (Execution & Results)
        print(">>> Creating PlacementTests Table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PlacementTests' AND xtype='U')
            CREATE TABLE PlacementTests (
                TestID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                TestDate DATETIME,
                TestType NVARCHAR(50), -- Online, Onsite
                AssignedAssessorID INT FOREIGN KEY REFERENCES Users_1(UserID),
                Status NVARCHAR(50) DEFAULT 'Pending', -- Pending, Completed
                ResultLevel NVARCHAR(50), -- A1, A2, etc.
                Feedback NVARCHAR(MAX),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)

        # 3. Training Offers Table (Level-Based Offers)
        print(">>> Creating TrainingOffers Table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainingOffers' AND xtype='U')
            CREATE TABLE TrainingOffers (
                OfferID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                TrainingLevel NVARCHAR(50),
                DeliveryMode NVARCHAR(50), -- Onsite, Online
                ClassTiming NVARCHAR(100),
                TrainingFee DECIMAL(18, 2),
                Status NVARCHAR(50) DEFAULT 'Pending', -- Accepted, Pending, Declined
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)

        # 4. Enrollments Table (Update/Create)
        print(">>> Updating Enrollments Table...")
        # Ensure Enrollments has necessary fields
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Enrollments' AND COLUMN_NAME='OfferID')
            BEGIN
                ALTER TABLE Enrollments ADD OfferID INT FOREIGN KEY REFERENCES TrainingOffers(OfferID);
                ALTER TABLE Enrollments ADD ExitInterviewStatus NVARCHAR(50); -- Completed, Pending
                ALTER TABLE Enrollments ADD ExitInterviewOutcome NVARCHAR(MAX);
                ALTER TABLE Enrollments ADD CompletionDate DATETIME;
            END
        """)

        # 5. Career Readiness Table (Post-Training)
        print(">>> Creating CareerReadiness Table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CareerReadiness' AND xtype='U')
            CREATE TABLE CareerReadiness (
                ReadinessID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                EnrollmentID INT FOREIGN KEY REFERENCES Enrollments(EnrollmentID),
                Status NVARCHAR(50), -- Eligible, Not Eligible, Deferred
                EvaluationDate DATETIME DEFAULT GETDATE(),
                Notes NVARCHAR(MAX)
            )
        """)

        conn.commit()
        print(">>> Database Updated Successfully for Training Workflow.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    update_training_schema()
