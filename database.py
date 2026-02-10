import sqlite3
import hashlib
import os
from datetime import datetime

DB_NAME = "place2026.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Users & Auth
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            PasswordHash TEXT NOT NULL,
            Role TEXT NOT NULL, -- Manager, Sales, Trainer, Corporate
            Department TEXT
        )
    ''')

    # 2. Corporate Clients & Requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clients (
            ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyName TEXT NOT NULL,
            Industry TEXT,
            ContactPerson TEXT,
            Phone TEXT,
            Email TEXT,
            Status TEXT DEFAULT 'Active',
            RequiredCount INTEGER DEFAULT 0,
            SalaryRange TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ClientRequests (
            RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientID INTEGER,
            JobTitle TEXT NOT NULL,
            NeededCount INTEGER DEFAULT 1,
            Requirements TEXT,
            Status TEXT DEFAULT 'Open', -- Open, Fulfilled, Cancelled
            RequestDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(ClientID) REFERENCES Clients(ClientID)
        )
    ''')

    # 3. Marketing & Campaigns (Linked to Requests)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Campaigns (
            CampaignID INTEGER PRIMARY KEY AUTOINCREMENT,
            RequestID INTEGER, -- Linked to a specific job request
            CampaignName TEXT NOT NULL,
            AdText TEXT, -- نص الإعلان
            Platform TEXT, -- Facebook, LinkedIn, etc.
            TargetAudience TEXT, -- المستهدف
            Budget REAL,
            StartDate DATE,
            EndDate DATE,
            Status TEXT DEFAULT 'Active',
            FOREIGN KEY(RequestID) REFERENCES ClientRequests(RequestID)
        )
    ''')

    # 4. Leads & Candidates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Interests (
            InterestID INTEGER PRIMARY KEY AUTOINCREMENT,
            CampaignID INTEGER, -- Source Campaign
            FullName TEXT NOT NULL,
            Phone TEXT,
            Email TEXT,
            Status TEXT DEFAULT 'New', -- New, Contacted, ExamScheduled, ConvertedToCandidate, Closed
            Source TEXT, -- Added Column for Lead Source
            Notes TEXT,
            RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(CampaignID) REFERENCES Campaigns(CampaignID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Candidates (
            CandidateID INTEGER PRIMARY KEY AUTOINCREMENT,
            InterestID INTEGER, -- Link back to lead
            FullName TEXT NOT NULL,
            NationalID TEXT,
            Phone TEXT,
            EducationLevel TEXT,
            Status TEXT DEFAULT 'New', -- New, PlacementScheduled, PlacementPassed, PlacementFailed, InTraining, ReadyForHire, Hired
            FOREIGN KEY(InterestID) REFERENCES Interests(InterestID)
        )
    ''')

    # 5. Placement Exams & Sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Exams (
            ExamID INTEGER PRIMARY KEY AUTOINCREMENT,
            ExamName TEXT NOT NULL, -- e.g. "English Placement Level 1"
            ExamType TEXT DEFAULT 'Placement', -- Placement, CourseFinal
            MaxScore INTEGER DEFAULT 100,
            PassScore INTEGER DEFAULT 70,
            Fee REAL DEFAULT 0
        )
    ''')
    
    # NEW: Exam Sessions (Available Slots)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ExamSessions (
            SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
            ExamID INTEGER,
            SessionDate DATETIME,
            MaxCapacity INTEGER DEFAULT 20,
            CurrentCount INTEGER DEFAULT 0,
            Status TEXT DEFAULT 'Open', -- Open, Full, Completed
            FOREIGN KEY(ExamID) REFERENCES Exams(ExamID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ExamAppointments (
            AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            CandidateID INTEGER,
            ExamID INTEGER,
            SessionID INTEGER, -- Linked to Session
            AppointmentDate DATETIME, -- Redundant if SessionID exists, but kept for direct flexibility
            Status TEXT DEFAULT 'Scheduled', -- Scheduled, Completed, NoShow
            Result INTEGER, -- Score
            ResultStatus TEXT, -- Passed, Failed
            IsPaid BOOLEAN DEFAULT 0,
            FOREIGN KEY(CandidateID) REFERENCES Candidates(CandidateID),
            FOREIGN KEY(ExamID) REFERENCES Exams(ExamID),
            FOREIGN KEY(SessionID) REFERENCES ExamSessions(SessionID)
        )
    ''')

    # 6. Training Management (Courses, Classes, Instructors)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Instructors (
            InstructorID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Specialty TEXT,
            Rate REAL DEFAULT 0 -- النسبة أو الأجر
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Trainings (
            TrainingID INTEGER PRIMARY KEY AUTOINCREMENT,
            TrainingName TEXT NOT NULL, -- e.g. "English Level A1 Course"
            InstructorID INTEGER,
            StartDate DATE,
            EndDate DATE,
            DaysSchedule TEXT, -- e.g. "Sun, Tue, Thu"
            Cost REAL DEFAULT 0,
            Status TEXT DEFAULT 'Planned', -- Planned, Active, Completed
            PrerequisiteLevel TEXT, -- المستوى التأهيلي المطلوب
            FOREIGN KEY(InstructorID) REFERENCES Instructors(InstructorID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TrainingEnrollments (
            EnrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            TrainingID INTEGER,
            CandidateID INTEGER,
            EnrollmentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            Status TEXT DEFAULT 'Active', -- Active, Dropped, Completed
            FinalGrade INTEGER,
            FOREIGN KEY(TrainingID) REFERENCES Trainings(TrainingID),
            FOREIGN KEY(CandidateID) REFERENCES Candidates(CandidateID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attendance (
            AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
            TrainingID INTEGER,
            CandidateID INTEGER,
            Date DATE,
            IsPresent BOOLEAN DEFAULT 0,
            FOREIGN KEY(TrainingID) REFERENCES Trainings(TrainingID),
            FOREIGN KEY(CandidateID) REFERENCES Candidates(CandidateID)
        )
    ''')

    # 7. Matching & Hiring
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Matches (
            MatchID INTEGER PRIMARY KEY AUTOINCREMENT,
            RequestID INTEGER,
            CandidateID INTEGER,
            MatchDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            Status TEXT DEFAULT 'Proposed', -- Proposed, Interviewing, Hired, Rejected
            FOREIGN KEY(RequestID) REFERENCES ClientRequests(RequestID),
            FOREIGN KEY(CandidateID) REFERENCES Candidates(CandidateID)
        )
    ''')

    # 8. Finance (Invoices & Receipts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Invoices (
            InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
            EntityID INTEGER, -- CandidateID or ClientID
            EntityType TEXT, -- 'Candidate' or 'Client'
            InvoiceType TEXT, -- 'PlacementExam', 'CourseFee', 'HiringFee'
            Description TEXT,
            Amount REAL NOT NULL,
            PaidAmount REAL DEFAULT 0,
            IssueDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            DueDate DATETIME,
            Status TEXT DEFAULT 'Unpaid' -- Unpaid, Partial, Paid
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Receipts (
            ReceiptID INTEGER PRIMARY KEY AUTOINCREMENT,
            InvoiceID INTEGER,
            Amount REAL NOT NULL,
            PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            ReceivedBy TEXT,
            Notes TEXT,
            FOREIGN KEY(InvoiceID) REFERENCES Invoices(InvoiceID)
        )
    ''')

    # Seed Data
    # 1. Users
    if not cursor.execute("SELECT * FROM Users").fetchone():
        users = [
            ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "Manager", "Management"),
            ("manager", hashlib.sha256("manager123".encode()).hexdigest(), "Manager", "Management"),
            ("sales", hashlib.sha256("sales123".encode()).hexdigest(), "Sales", "Sales"),
            ("corporate", hashlib.sha256("corp123".encode()).hexdigest(), "Corporate", "Corporate"),
            ("trainer", hashlib.sha256("trainer123".encode()).hexdigest(), "Trainer", "Training"),
        ]
        cursor.executemany("INSERT INTO Users (Username, PasswordHash, Role, Department) VALUES (?, ?, ?, ?)", users)
    else:
        # Check if admin exists, if not add it (Migration fix)
        if not cursor.execute("SELECT * FROM Users WHERE Username = 'admin'").fetchone():
            cursor.execute("INSERT INTO Users (Username, PasswordHash, Role, Department) VALUES (?, ?, ?, ?)", 
                          ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "Manager", "Management"))
    
    # 2. Basic Exams & Instructors
    if not cursor.execute("SELECT * FROM Exams").fetchone():
        cursor.execute("INSERT INTO Exams (ExamName, ExamType, MaxScore, PassScore) VALUES ('English Placement Test', 'Placement', 100, 70)")
        cursor.execute("INSERT INTO Exams (ExamName, ExamType, MaxScore, PassScore) VALUES ('IQ Test', 'Placement', 100, 60)")
    
    # Migrations (Add Columns if missing)
    try:
        cursor.execute("ALTER TABLE Instructors ADD COLUMN Rate REAL DEFAULT 0")
    except sqlite3.OperationalError: pass

    try:
        cursor.execute("ALTER TABLE Trainings ADD COLUMN PrerequisiteLevel TEXT")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE Interests ADD COLUMN Source TEXT")
    except sqlite3.OperationalError: pass

    try:
        cursor.execute("ALTER TABLE Clients ADD COLUMN RequiredCount INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE Clients ADD COLUMN SalaryRange TEXT")
    except sqlite3.OperationalError: pass

    try:
        cursor.execute("ALTER TABLE Exams ADD COLUMN Fee REAL DEFAULT 0")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE ExamAppointments ADD COLUMN SessionID INTEGER")
        cursor.execute("ALTER TABLE ExamAppointments ADD COLUMN IsPaid BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass

    if not cursor.execute("SELECT * FROM Instructors").fetchone():
        cursor.execute("INSERT INTO Instructors (Name, Specialty, Rate) VALUES ('Mr. Ahmed English', 'English', 20.0)")
        cursor.execute("INSERT INTO Instructors (Name, Specialty, Rate) VALUES ('Dr. Sarah SoftSkills', 'Soft Skills', 25.0)")

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password):
    conn = get_db_connection()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    user = conn.execute("SELECT * FROM Users WHERE Username = ? AND PasswordHash = ?", (username, pwd_hash)).fetchone()
    conn.close()
    return user

# Helper functions
def fetch_all(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def exec_non_query(query, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

# Specific getters
def get_all_clients():
    return fetch_all("SELECT * FROM Clients")

def get_campaigns():
    return fetch_all("SELECT c.*, r.JobTitle FROM Campaigns c LEFT JOIN ClientRequests r ON c.RequestID = r.RequestID")

def get_all_interests():
    return fetch_all("SELECT i.*, c.CampaignName FROM Interests i LEFT JOIN Campaigns c ON i.CampaignID = c.CampaignID")

def get_pending_invoices():
    return fetch_all("SELECT * FROM Invoices WHERE Status != 'Paid'")

def get_all_trainings():
    return fetch_all("SELECT t.*, i.Name as InstructorName FROM Trainings t LEFT JOIN Instructors i ON t.InstructorID = i.InstructorID")

def get_all_instructors():
    return fetch_all("SELECT * FROM Instructors")

def get_placement_exams():
    return fetch_all("SELECT * FROM Exams WHERE ExamType = 'Placement'")

def get_all_candidates():
    return fetch_all("SELECT * FROM Candidates")

def get_dashboard_stats():
    # Simple stats for dashboard
    total_cand = fetch_all("SELECT COUNT(*) as c FROM Candidates")[0]['c']
    hired = fetch_all("SELECT COUNT(*) as c FROM Candidates WHERE Status = 'Hired'")[0]['c']
    
    # Exam Success Rate
    passed = fetch_all("SELECT COUNT(*) as c FROM ExamAppointments WHERE ResultStatus = 'Passed'")[0]['c']
    total_exams = fetch_all("SELECT COUNT(*) as c FROM ExamAppointments WHERE ResultStatus IS NOT NULL")[0]['c']
    rate = round((passed / total_exams * 100) if total_exams > 0 else 0, 1)

    return {
        'total_candidates': total_cand,
        'hired_candidates': hired,
        'exam_success_rate': rate
    }

def get_sales_dashboard():
    # Simple stats for sales
    total_leads = fetch_all("SELECT COUNT(*) as c FROM Interests")[0]['c']
    today = datetime.now().strftime('%Y-%m-%d')
    today_leads = fetch_all(f"SELECT COUNT(*) as c FROM Interests WHERE date(RegistrationDate) = '{today}'")[0]['c']
    contacted = fetch_all("SELECT COUNT(*) as c FROM Interests WHERE Status != 'New'")[0]['c']
    
    return {
        'total_leads': total_leads,
        'today_leads': today_leads,
        'contacted_leads': contacted,
        'conversion_rate': 0 # Placeholder
    }

def get_requests_by_client(client_id):
    return fetch_all("SELECT * FROM ClientRequests WHERE ClientID = ?", (client_id,))

def get_exam_sessions(exam_id=None):
    if exam_id:
        return fetch_all("SELECT * FROM ExamSessions WHERE ExamID = ? AND Status = 'Open' ORDER BY SessionDate", (exam_id,))
    return fetch_all("SELECT s.*, e.ExamName FROM ExamSessions s JOIN Exams e ON s.ExamID = e.ExamID WHERE s.Status = 'Open' ORDER BY s.SessionDate")

def get_exam_enrollments(session_id):
     return fetch_all("SELECT a.*, c.FullName FROM ExamAppointments a JOIN Candidates c ON a.CandidateID = c.CandidateID WHERE a.SessionID = ?", (session_id,))

# --- CRUD Functions ---

def add_client(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Clients ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_client_request(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO ClientRequests ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_campaign(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Campaigns ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_interest_registration(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Interests ({keys}) VALUES ({placeholders})", tuple(data.values()))

def convert_interest_to_candidate(interest_id):
    # Check if already exists
    existing = fetch_all("SELECT CandidateID FROM Candidates WHERE InterestID = ?", (interest_id,))
    if existing:
        return existing[0]['CandidateID']
    
    # Get interest data
    interest = fetch_all("SELECT * FROM Interests WHERE InterestID = ?", (interest_id,))[0]
    
    # Create Candidate
    cand_data = {
        "InterestID": interest_id,
        "FullName": interest['FullName'],
        "Phone": interest['Phone'],
        "Status": "New"
    }
    
    keys = ', '.join(cand_data.keys())
    placeholders = ', '.join(['?'] * len(cand_data))
    cand_id = exec_non_query(f"INSERT INTO Candidates ({keys}) VALUES ({placeholders})", tuple(cand_data.values()))
    
    # Update Interest Status
    exec_non_query("UPDATE Interests SET Status = 'ConvertedToCandidate' WHERE InterestID = ?", (interest_id,))
    
    return cand_id

def create_invoice(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Invoices ({keys}) VALUES ({placeholders})", tuple(data.values()))

def match_candidate_to_request(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Matches ({keys}) VALUES ({placeholders})", tuple(data.values()))

def schedule_exam(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    # Update session count if SessionID is present
    if "SessionID" in data and data["SessionID"]:
        exec_non_query("UPDATE ExamSessions SET CurrentCount = CurrentCount + 1 WHERE SessionID = ?", (data["SessionID"],))
        
    return exec_non_query(f"INSERT INTO ExamAppointments ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_exam_session(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO ExamSessions ({keys}) VALUES ({placeholders})", tuple(data.values()))

def enroll_candidate(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO TrainingEnrollments ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_receipt(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Receipts ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_instructor(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Instructors ({keys}) VALUES ({placeholders})", tuple(data.values()))

def add_training(data):
    keys = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    return exec_non_query(f"INSERT INTO Trainings ({keys}) VALUES ({placeholders})", tuple(data.values()))

# Init on load
init_db()
