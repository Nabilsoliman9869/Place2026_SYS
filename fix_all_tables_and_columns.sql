-- ============================================================
-- تصحيح الجداول والأعمدة الناقصة في قاعدة البيانات
-- شغّل هذا السكربت مرة واحدة على SQL Server (محلي أو Render).
-- غيّر اسم القاعدة في USE إذا لزم الأمر.
-- ============================================================

-- USE Place2026DB;
-- GO

-- ========== 1. جدول Matches — أعمدة ناقصة ==========
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'AllocatorID')
    ALTER TABLE Matches ADD AllocatorID INT NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'ReviewNotes')
    ALTER TABLE Matches ADD ReviewNotes NVARCHAR(MAX) NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'AllocatorFeedback')
    ALTER TABLE Matches ADD AllocatorFeedback NVARCHAR(MAX) NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'InterviewDate')
    ALTER TABLE Matches ADD InterviewDate DATETIME NULL;

-- ========== 2. جدول Candidates — أعمدة ناقصة ==========
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Candidates') AND name = 'RecruiterID')
    ALTER TABLE Candidates ADD RecruiterID INT NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Candidates') AND name = 'AllocatorID')
    ALTER TABLE Candidates ADD AllocatorID INT NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Candidates') AND name = 'Rejoiner')
    ALTER TABLE Candidates ADD Rejoiner BIT DEFAULT 0 NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Candidates') AND name = 'PrimaryIntent')
    ALTER TABLE Candidates ADD PrimaryIntent NVARCHAR(50) NULL;

-- ========== 3. جدول Schedules (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'Schedules' AND xtype = 'U')
BEGIN
    CREATE TABLE Schedules (
        ScheduleID INT IDENTITY(1,1) PRIMARY KEY,
        Context NVARCHAR(50) NOT NULL,
        OwnerUserID INT NULL,
        OwnerClientID INT NULL,
        SlotDate DATE NOT NULL,
        SlotTime NVARCHAR(10) NOT NULL,
        Status NVARCHAR(50) NULL,
        BookedCandidateID INT NULL,
        BookingMode NVARCHAR(50) NULL,
        MeetingLink NVARCHAR(MAX) NULL,
        Notes NVARCHAR(MAX) NULL,
        CreatedAt DATETIME NULL,
        IsConfirmedByRecruiter BIT NULL
    );
END

-- ========== 4. جدول TASchedules (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'TASchedules' AND xtype = 'U')
BEGIN
    CREATE TABLE TASchedules (
        SlotID INT IDENTITY(1,1) PRIMARY KEY,
        SlotDate DATE NOT NULL,
        SlotTime NVARCHAR(10) NOT NULL,
        Status NVARCHAR(50) NULL,
        Type NVARCHAR(50) NULL,
        CandidateID INT NULL,
        BookedBy INT NULL,
        EvaluatorID INT NULL,
        Notes NVARCHAR(MAX) NULL,
        CreatedAt DATETIME NULL,
        InterviewType NVARCHAR(50) NULL,
        IsConfirmedByRecruiter BIT NULL
    );
END

-- ========== 5. جدول Evaluations (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'Evaluations' AND xtype = 'U')
BEGIN
    CREATE TABLE Evaluations (
        EvaluationID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT NULL,
        SlotID INT NULL,
        Score_Comprehension INT NULL,
        Score_Fluency INT NULL,
        Score_Pronunciation INT NULL,
        Score_Structure INT NULL,
        Score_Vocabulary INT NULL,
        CEFR_Level NVARCHAR(10) NULL,
        Decision NVARCHAR(50) NULL,
        RecommendedLevel NVARCHAR(50) NULL,
        Comments NVARCHAR(MAX) NULL,
        EvaluatorID INT NULL,
        EvaluationDate DATETIME NULL,
        EvaluationType NVARCHAR(50) NULL,
        RecordingLink NVARCHAR(500) NULL
    );
END
ELSE
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Evaluations') AND name = 'EvaluationType')
        ALTER TABLE Evaluations ADD EvaluationType NVARCHAR(50) NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Evaluations') AND name = 'RecordingLink')
        ALTER TABLE Evaluations ADD RecordingLink NVARCHAR(500) NULL;
END

-- ========== 6. جدول Notifications (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'Notifications' AND xtype = 'U')
BEGIN
    CREATE TABLE Notifications (
        NotificationID INT IDENTITY(1,1) PRIMARY KEY,
        UserID INT NULL,
        Message NVARCHAR(MAX) NULL,
        Type NVARCHAR(50) NULL,
        RelatedID INT NULL,
        IsRead BIT NULL,
        CreatedAt DATETIME NULL
    );
END

-- ========== 7. جدول RecruitmentFailures (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'RecruitmentFailures' AND xtype = 'U')
BEGIN
    CREATE TABLE RecruitmentFailures (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT NULL,
        Stage NVARCHAR(50) NULL,
        Reason NVARCHAR(MAX) NULL,
        LoggedBy INT NULL,
        CreatedAt DATETIME NULL
    );
END

-- ========== 8. جدول ClientInterviews (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'ClientInterviews' AND xtype = 'U')
BEGIN
    CREATE TABLE ClientInterviews (
        InterviewID INT IDENTITY(1,1) PRIMARY KEY,
        MatchID INT NULL,
        InterviewDate DATETIME NULL,
        Status NVARCHAR(50) NULL,
        Feedback NVARCHAR(MAX) NULL,
        RejectionReason NVARCHAR(MAX) NULL,
        ActionRequired NVARCHAR(MAX) NULL,
        RecordedBy INT NULL
    );
END

-- ========== 9. جدول HiringRecords (إن لم يكن موجوداً) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'HiringRecords' AND xtype = 'U')
BEGIN
    CREATE TABLE HiringRecords (
        HiringRecordID INT IDENTITY(1,1) PRIMARY KEY,
        MatchID INT NOT NULL,
        StartDate DATE NULL,
        Salary DECIMAL(18,2) NULL,
        ContractType NVARCHAR(50) NULL,
        CreatedBy INT NULL,
        CreatedAt DATETIME DEFAULT GETDATE() NULL
    );
END

-- ========== 10. جدول TraineeSheetData (بيانات الأوراق لكل متدرب) ==========
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'TraineeSheetData' AND xtype = 'U')
BEGIN
    CREATE TABLE TraineeSheetData (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT NOT NULL,
        SheetName NVARCHAR(100) NOT NULL,
        JsonData NVARCHAR(MAX) NULL,
        UpdatedAt DATETIME DEFAULT GETDATE() NULL
    );
END

PRINT 'تم تنفيذ تصحيح الجداول والأعمدة بنجاح.';
