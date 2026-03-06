-- ============================================================
-- إدراج مستخدم مبيعات التدريب train_sales (وباقي مستخدمي التدريب) في Users_1
-- نفّذ هذا السكربت مرة واحدة على قاعدة البيانات (محلي أو Render).
-- ============================================================

-- التأكد من وجود الجدول (إن لم يكن موجوداً أنشئه يدوياً أو شغّل fix_all_tables_and_columns.sql أولاً)
-- الجدول: Users_1 (UserID, Username, Password, Role, FullName [, Email, CreatedAt])

-- 1) train_sales — مبيعات التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'train_sales')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'train_sales', N'123', N'TrainingSales', N'مبيعات التدريب');
    PRINT 'تم إضافة train_sales';
END
ELSE
    PRINT 'train_sales موجود مسبقاً';

-- 2) ta_train — مختبر مواهب التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'ta_train')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'ta_train', N'123', N'Talent_Training', N'مختبر مواهب التدريب');
    PRINT 'تم إضافة ta_train';
END
ELSE
    PRINT 'ta_train موجود مسبقاً';

-- 3) train_coord — منسق التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'train_coord')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'train_coord', N'123', N'TrainingCoordinator', N'منسق التدريب');
    PRINT 'تم إضافة train_coord';
END
ELSE
    PRINT 'train_coord موجود مسبقاً';

-- 4) train_mgr — مدير التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'train_mgr')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'train_mgr', N'123', N'TrainingManager', N'مدير التدريب');
    PRINT 'تم إضافة train_mgr';
END
ELSE
    PRINT 'train_mgr موجود مسبقاً';

-- 5) train_head — رئيس قسم التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'train_head')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'train_head', N'123', N'TrainingHead', N'رئيس قسم التدريب');
    PRINT 'تم إضافة train_head';
END
ELSE
    PRINT 'train_head موجود مسبقاً';

-- 6) train_lead — قائد التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'train_lead')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'train_lead', N'123', N'TrainingLead', N'قائد التدريب');
    PRINT 'تم إضافة train_lead';
END
ELSE
    PRINT 'train_lead موجود مسبقاً';

-- 7) trainer1 — مدرب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'trainer1')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'trainer1', N'123', N'Trainer', N'مدرب');
    PRINT 'تم إضافة trainer1';
END
ELSE
    PRINT 'trainer1 موجود مسبقاً';

-- التحقق: عرض كل المستخدمين في Users_1
SELECT UserID, Username, Role, FullName FROM Users_1 ORDER BY UserID;

-- ========== إذا فشل الإدراج (عمود FullName غير موجود) استخدم أحد الأمرين التاليين يدوياً ==========
-- INSERT INTO Users_1 (Username, Password, Role) VALUES (N'train_sales', N'123', N'TrainingSales');
-- ثم تحقق: SELECT * FROM Users_1 WHERE Username = N'train_sales';
