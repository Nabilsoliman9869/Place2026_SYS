import sqlite3
import hashlib
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

    # 2. Corporate Clients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clients (
            ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyName TEXT NOT NULL,
            Industry TEXT,
            ContactPerson TEXT,
            Phone TEXT,
            Email TEXT,
            Address TEXT,
            Status TEXT DEFAULT 'Active',
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Client Requests (Job Orders)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ClientRequests (
            RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientID INTEGER,
            JobTitle TEXT NOT NULL,
            NeededCount INTEGER DEFAULT 1,
            Requirements TEXT, -- Detailed job requirements
            SalaryRange TEXT,
            Status TEXT DEFAULT 'Open', -- Open, Fulfilled, Cancelled
            RequestDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(ClientID) REFERENCES Clients(ClientID)
        )
    ''')

    # 4. Marketing Campaigns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Campaigns (
            CampaignID INTEGER PRIMARY KEY AUTOINCREMENT,
            RequestID INTEGER, -- Linked to a specific job request
            CampaignName TEXT NOT NULL,
            Platform TEXT, -- Facebook, LinkedIn, etc.
            AdText TEXT,
            TargetAudience TEXT,
            Budget REAL DEFAULT 0,
            StartDate DATE,
            EndDate DATE,
            Status TEXT DEFAULT 'Active',
            FOREIGN KEY(RequestID) REFERENCES ClientRequests(RequestID)
        )
    ''')

    # 5. Leads (Interests)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Interests (
            InterestID INTEGER PRIMARY KEY AUTOINCREMENT,
            CampaignID INTEGER,
            FullName TEXT NOT NULL,
            Phone TEXT,
            Email TEXT,
            Source TEXT,
            Notes TEXT,
            Status TEXT DEFAULT 'New', -- New, Contacted, ExamScheduled, ConvertedToCandidate, Closed
            RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(CampaignID) REFERENCES Campaigns(CampaignID)
        )
    ''')

    # 6. Candidates (Official Profile)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Candidates (
            CandidateID INTEGER PRIMARY KEY AUTOINCREMENT,
            InterestID INTEGER, -- Link back to lead
            FullName TEXT NOT NULL,
            NationalID TEXT,
            Phone TEXT,
            Email TEXT,
            EducationLevel TEXT,
            Status TEXT DEFAULT 'New', -- New, PlacementScheduled, PlacementPassed, PlacementFailed, InTraining, ReadyForHire, Hired
            FOREIGN KEY(InterestID) REFERENCES Interests(InterestID)
        )
    ''')

    # 7. Placement Exams & Sessions
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
            SessionID INTEGER,
            Status TEXT DEFAULT 'Scheduled', -- Scheduled, Completed, NoShow
            Result INTEGER, -- Score
            ResultStatus TEXT, -- Passed, Failed
            IsPaid BOOLEAN DEFAULT 0,
            FOREIGN KEY(CandidateID) REFERENCES Candidates(CandidateID),
            FOREIGN KEY(ExamID) REFERENCES Exams(ExamID),
            FOREIGN KEY(SessionID) REFERENCES ExamSessions(SessionID)
        )
    ''')

    # 8. Training Management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Instructors (
            InstructorID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Specialty TEXT,
            Rate REAL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Trainings (
            TrainingID INTEGER PRIMARY KEY AUTOINCREMENT,
            TrainingName TEXT NOT NULL,
            InstructorID INTEGER,
            StartDate DATE,
            EndDate DATE,
            DaysSchedule TEXT,
            Cost REAL DEFAULT 0,
            Status TEXT DEFAULT 'Planned', -- Planned, Active, Completed
            PrerequisiteLevel TEXT,
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

    # 9. Matching & Hiring
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

    # 10. Finance
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

    # Seed Data - Users
    if not cursor.execute("SELECT * FROM Users").fetchone():
        users = [
            ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "Manager", "Management"),
            ("manager", hashlib.sha256("manager123".encode()).hexdigest(), "Manager", "Management"),
            ("sales", hashlib.sha256("sales123".encode()).hexdigest(), "Sales", "Sales"),
            ("corporate", hashlib.sha256("corp123".encode()).hexdigest(), "Corporate", "Corporate"),
            ("trainer", hashlib.sha256("trainer123".encode()).hexdigest(), "Trainer", "Training"),
        ]
        cursor.executemany("INSERT INTO Users (Username, PasswordHash, Role, Department) VALUES (?, ?, ?, ?)", users)

    # Seed Data - Basic Exams
    if not cursor.execute("SELECT * FROM Exams").fetchone():
        cursor.execute("INSERT INTO Exams (ExamName, ExamType, MaxScore, PassScore, Fee) VALUES ('English Placement Test', 'Placement', 100, 70, 100)")
        cursor.execute("INSERT INTO Exams (ExamName, ExamType, MaxScore, PassScore, Fee) VALUES ('IQ Test', 'Placement', 100, 60, 150)")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
