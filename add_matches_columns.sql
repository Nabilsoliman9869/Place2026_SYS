-- ============================================================
-- إضافة الأعمدة الناقصة لجدول Matches (لتفادي Internal Server Error عند Confirm & Create Match)
-- شغّل هذا السكربت مرة واحدة على قاعدة البيانات (SQL Server) المحلية أو على Render.
-- ============================================================

USE Place2026DB;  -- غيّر اسم القاعدة إذا كانت مختلفة عندك
GO

-- AllocatorID: من قام بالموافقة على الترشيح
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'AllocatorID')
BEGIN
    ALTER TABLE Matches ADD AllocatorID INT NULL;
    PRINT 'Added column: AllocatorID';
END
ELSE PRINT 'Column AllocatorID already exists.';

-- ReviewNotes: ملاحظات داخلية للمُراجع
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'ReviewNotes')
BEGIN
    ALTER TABLE Matches ADD ReviewNotes NVARCHAR(MAX) NULL;
    PRINT 'Added column: ReviewNotes';
END
ELSE PRINT 'Column ReviewNotes already exists.';

-- AllocatorFeedback: ملاحظات للمُرشّح (تظهر له)
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'Matches') AND name = 'AllocatorFeedback')
BEGIN
    ALTER TABLE Matches ADD AllocatorFeedback NVARCHAR(MAX) NULL;
    PRINT 'Added column: AllocatorFeedback';
END
ELSE PRINT 'Column AllocatorFeedback already exists.';

GO
