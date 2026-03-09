-- إضافة أعمدة تكوين الدفعة والحضور إن لم تكن موجودة
-- نفّذ على قاعدة الإنتاج (Render) إذا واجهت Internal Server Error

-- CourseBatches
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'StartTime')
    ALTER TABLE CourseBatches ADD StartTime TIME NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'EndTime')
    ALTER TABLE CourseBatches ADD EndTime TIME NULL;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'CourseBatches') AND Name = N'WeekDays')
    ALTER TABLE CourseBatches ADD WeekDays NVARCHAR(100) NULL;

-- Attendance (الحضور التفصيلي)
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'Attendance') AND Name = N'CheckInTime')
    ALTER TABLE Attendance ADD CheckInTime TIME;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'Attendance') AND Name = N'CheckOutTime')
    ALTER TABLE Attendance ADD CheckOutTime TIME;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'Attendance') AND Name = N'TotalHours')
    ALTER TABLE Attendance ADD TotalHours DECIMAL(5,2);
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'Attendance') AND Name = N'AssignmentDone')
    ALTER TABLE Attendance ADD AssignmentDone BIT DEFAULT 0;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Object_ID = Object_ID(N'Attendance') AND Name = N'LateMinutes')
    ALTER TABLE Attendance ADD LateMinutes INT NULL;

PRINT 'تم التحقق من أعمدة CourseBatches و Attendance.';
