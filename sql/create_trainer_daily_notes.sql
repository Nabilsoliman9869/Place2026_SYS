-- إنشاء جدول ملاحظات المدرب اليومية (للعروض الحية التي لم تُنفّذ فيها init_system بعد)
-- Run this once if TrainerDailyNotes does not exist.

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'TrainerDailyNotes' AND xtype = 'U')
BEGIN
    CREATE TABLE TrainerDailyNotes (
        NoteID INT IDENTITY(1,1) PRIMARY KEY,
        EnrollmentID INT NOT NULL,
        NoteDate DATE NOT NULL,
        Notes NVARCHAR(MAX) NOT NULL,
        TrainerID INT NULL,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO
