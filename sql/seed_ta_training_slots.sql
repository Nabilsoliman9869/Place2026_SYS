-- ============================================================
-- شاغر اختبار مواهب التدريب: مستخدم Talent_Training + مواعيد TASchedules
-- نفّذ هذا السكربت على قاعدة الإنتاج (مثلاً Render) مرة واحدة حتى تظهر «الشاغر المتاحة» عند حجز موعد اختبار تدريب.
-- ============================================================

-- 1) التأكد من وجود مستخدم مختبر مواهب التدريب
IF NOT EXISTS (SELECT 1 FROM Users_1 WHERE Username = N'ta_train')
BEGIN
    INSERT INTO Users_1 (Username, Password, Role, FullName)
    VALUES (N'ta_train', N'123', N'Talent_Training', N'مختبر مواهب التدريب');
    PRINT N'تم إضافة ta_train (Talent_Training)';
END
ELSE
    PRINT N'ta_train موجود';

-- 2) إدراج مواعيد TASchedules: كل 15 دقيقة من 10 ص إلى 9 م، لمدة 14 يوماً، لكل مستخدم بدور Talent_Training
-- (يُستبعد المواعيد الموجودة مسبقاً)
;WITH Evaluators AS (
    SELECT UserID FROM Users_1 WHERE Role IN (N'Talent_Training', N'TA-Training')
),
Days AS (
    SELECT n FROM (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13)) AS T(n)
),
Slots AS (
    SELECT s FROM (VALUES
        (N'10:00'),(N'10:15'),(N'10:30'),(N'10:45'),(N'11:00'),(N'11:15'),(N'11:30'),(N'11:45'),
        (N'12:00'),(N'12:15'),(N'12:30'),(N'12:45'),(N'13:00'),(N'13:15'),(N'13:30'),(N'13:45'),
        (N'14:00'),(N'14:15'),(N'14:30'),(N'14:45'),(N'15:00'),(N'15:15'),(N'15:30'),(N'15:45'),
        (N'16:00'),(N'16:15'),(N'16:30'),(N'16:45'),(N'17:00'),(N'17:15'),(N'17:30'),(N'17:45'),
        (N'18:00'),(N'18:15'),(N'18:30'),(N'18:45'),(N'19:00'),(N'19:15'),(N'19:30'),(N'19:45'),
        (N'20:00'),(N'20:15'),(N'20:30'),(N'20:45'),(N'21:00')
    ) AS T(s)
)
INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID)
SELECT 
    DATEADD(day, d.n, CAST(GETDATE() AS DATE)) AS SlotDate,
    s.s AS SlotTime,
    N'Available' AS Status,
    e.UserID AS EvaluatorID
FROM Evaluators e
CROSS JOIN Days d
CROSS JOIN Slots s
WHERE NOT EXISTS (
    SELECT 1 FROM TASchedules T 
    WHERE T.EvaluatorID = e.UserID 
      AND T.SlotDate = DATEADD(day, d.n, CAST(GETDATE() AS DATE)) 
      AND T.SlotTime = s.s
);

PRINT N'تم إدراج مواعيد TASchedules (10 ص - 9 م كل 15 دقيقة، 14 يوماً). جرّب «حجز موعد اختبار مواهب تدريب» من لوحة مبيعات التدريب.';
GO
