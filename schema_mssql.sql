-- Place 2026 Database Schema for SQL Server (Updated)

-- Users Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(50) NOT NULL UNIQUE,
        Password NVARCHAR(100) NOT NULL,
        Role NVARCHAR(50) NOT NULL
    );
    INSERT INTO Users (Username, Password, Role) VALUES 
    ('manager', 'manager123', 'Manager'),
    ('sales', 'sales123', 'Sales'),
    ('corporate', 'corp123', 'Corporate'),
    ('trainer', 'trainer123', 'Trainer'),
    ('dev', '123', 'Developer');
END
GO

-- Clients Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clients' AND xtype='U')
BEGIN
    CREATE TABLE Clients (
        ClientID INT IDENTITY(1,1) PRIMARY KEY,
        CompanyName NVARCHAR(100) NOT NULL,
        Industry NVARCHAR(100),
        ContactPerson NVARCHAR(100),
        Email NVARCHAR(100),
        Phone NVARCHAR(50),
        Address NVARCHAR(MAX),
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- ClientRequests Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
BEGIN
    CREATE TABLE ClientRequests (
        RequestID INT IDENTITY(1,1) PRIMARY KEY,
        ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
        JobTitle NVARCHAR(100) NOT NULL,
        Requirements NVARCHAR(MAX),
        NeededCount INT DEFAULT 1,
        Status NVARCHAR(50) DEFAULT 'Open',
        Gender NVARCHAR(20),
        SalaryFrom DECIMAL(18,2),
        SalaryTo DECIMAL(18,2),
        Benefits NVARCHAR(MAX),
        SoftSkills NVARCHAR(MAX),
        EnglishLevel NVARCHAR(10),
        ThirdLanguage NVARCHAR(50),
        ComputerLevel NVARCHAR(50),
        Location NVARCHAR(50),
        AgeFrom INT,
        AgeTo INT,
        PhysicalTraits NVARCHAR(MAX),
        Smoker NVARCHAR(20),
        AppearanceLevel NVARCHAR(50),
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- Campaigns Table (Updated for Types)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Campaigns' AND xtype='U')
BEGIN
    CREATE TABLE Campaigns (
        CampaignID INT IDENTITY(1,1) PRIMARY KEY,
        RequestID INT NULL FOREIGN KEY REFERENCES ClientRequests(RequestID),
        Name NVARCHAR(100),
        Type NVARCHAR(20) DEFAULT 'Linked',
        MediaChannel NVARCHAR(100),
        AdText NVARCHAR(MAX),
        TargetAudience NVARCHAR(MAX),
        Budget DECIMAL(18, 2),
        StartDate DATE,
        EndDate DATE,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
ELSE
BEGIN
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Type' AND Object_ID = Object_ID(N'Campaigns'))
        ALTER TABLE Campaigns ADD Type NVARCHAR(20) DEFAULT 'Linked';
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Name' AND Object_ID = Object_ID(N'Campaigns'))
        ALTER TABLE Campaigns ADD Name NVARCHAR(100);
    ALTER TABLE Campaigns ALTER COLUMN RequestID INT NULL;
END
GO

-- ExamSlots Table (New - For Training Dept)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ExamSlots' AND xtype='U')
BEGIN
    CREATE TABLE ExamSlots (
        SlotID INT IDENTITY(1,1) PRIMARY KEY,
        SlotDate DATE,
        TimeFrom TIME,
        TimeTo TIME,
        Type NVARCHAR(50),
        Cost DECIMAL(18,2) DEFAULT 0,
        MaxCapacity INT DEFAULT 10,
        ReservedCount INT DEFAULT 0,
        Status NVARCHAR(20) DEFAULT 'Available'
    );
END
GO

-- Candidates Table (Leads) - Enhanced for CRM
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
BEGIN
    CREATE TABLE Candidates (
        CandidateID INT IDENTITY(1,1) PRIMARY KEY,
        FullName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100),
        Phone NVARCHAR(50),
        Status NVARCHAR(50) DEFAULT 'Lead',
        Source NVARCHAR(100),
        CampaignID INT NULL FOREIGN KEY REFERENCES Campaigns(CampaignID),
        LastContactDate DATETIME,
        NextFollowUpDate DATETIME,
        Feedback NVARCHAR(MAX),
        InterestLevel NVARCHAR(20),
        ExamSlotID INT NULL FOREIGN KEY REFERENCES ExamSlots(SlotID),
        ExamResult NVARCHAR(50),
        EvaluationDetails NVARCHAR(MAX),
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
ELSE
BEGIN
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CampaignID' AND Object_ID = Object_ID(N'Candidates'))
        ALTER TABLE Candidates ADD CampaignID INT NULL FOREIGN KEY REFERENCES Campaigns(CampaignID);
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'NextFollowUpDate' AND Object_ID = Object_ID(N'Candidates'))
        ALTER TABLE Candidates ADD NextFollowUpDate DATETIME;
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'ExamSlotID' AND Object_ID = Object_ID(N'Candidates'))
        ALTER TABLE Candidates ADD ExamSlotID INT NULL FOREIGN KEY REFERENCES ExamSlots(SlotID);
END
GO

-- Exams Definitions
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Exams' AND xtype='U')
BEGIN
    CREATE TABLE Exams (
        ExamID INT IDENTITY(1,1) PRIMARY KEY,
        ExamName NVARCHAR(100) NOT NULL,
        Type NVARCHAR(50),
        Description NVARCHAR(MAX),
        Cost DECIMAL(18, 2)
    );
END
GO

-- Invoices Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Invoices' AND xtype='U')
BEGIN
    CREATE TABLE Invoices (
        InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
        Amount DECIMAL(18, 2),
        IssueDate DATE DEFAULT GETDATE(),
        Status NVARCHAR(50) DEFAULT 'Unpaid'
    );
END
GO
