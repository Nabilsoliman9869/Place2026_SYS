-- ============================================================
-- جدول ملاحظات المدرب اليومية (جدول تفاصيل)
-- فيه حقل المتدرب (CandidateID) = مين الجايد
-- شغّله مرة واحدة على القاعدة إذا ظهر: Invalid object name 'TrainerDailyNotes'
-- ============================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'TrainerDailyNotes' AND xtype = 'U')
BEGIN
    CREATE TABLE TrainerDailyNotes (
        NoteID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT NOT NULL,
        EnrollmentID INT NOT NULL,
        NoteDate DATE NOT NULL,
        Notes NVARCHAR(MAX) NOT NULL,
        TrainerID INT NULL,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
    PRINT 'Table TrainerDailyNotes created (with CandidateID = المتدرب).';
END
ELSE
BEGIN
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('TrainerDailyNotes') AND name = 'CandidateID')
    BEGIN
        ALTER TABLE TrainerDailyNotes ADD CandidateID INT NULL;
        UPDATE N SET N.CandidateID = E.CandidateID FROM TrainerDailyNotes N INNER JOIN Enrollments E ON N.EnrollmentID = E.EnrollmentID;
        PRINT 'Column CandidateID (المتدرب) added to TrainerDailyNotes.';
    END
    ELSE
        PRINT 'Table TrainerDailyNotes already exists with CandidateID.';
END
GO
