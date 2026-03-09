-- إضافة أعمدة تكوين الدفعة إن لم تكن موجودة
-- نفّذ على قاعدة الإنتاج (Render) إذا واجهت Internal Server Error عند إضافة Wave

-- التحقق يدوياً: إذا ظهر خطأ "Invalid column name" عند التنفيذ فالأعمدة غير موجودة
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'StartTime')
    ALTER TABLE CourseBatches ADD StartTime TIME NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'EndTime')
    ALTER TABLE CourseBatches ADD EndTime TIME NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'WeekDays')
    ALTER TABLE CourseBatches ADD WeekDays NVARCHAR(100) NULL;

PRINT 'تم التحقق من أعمدة CourseBatches.';
