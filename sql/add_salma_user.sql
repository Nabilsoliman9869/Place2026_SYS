-- إضافة مستخدم SALMA بصلاحيات مبيعات+منسق تدريب
-- كلمة المرور: 123
-- نفّذ هذا السكربت في SQL Server Management Studio أو sqlcmd

IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = 'salma')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'salma', N'123', N'TrainingSalesCoordinator', N'سلمى');
    PRINT 'تم إضافة المستخدم salma بنجاح.';
END
ELSE
BEGIN
    PRINT 'المستخدم salma موجود مسبقاً.';
END
