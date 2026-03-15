-- تكبير عمود AllocatorRole ليدعم قيماً متعددة (أدوار مفصولة بفاصلة)
-- للمخول بالترشيح — اختيار أكثر من دور في طلب العميل

IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'AllocatorRole' AND Object_ID = Object_ID(N'ClientRequests'))
BEGIN
    ALTER TABLE ClientRequests ADD AllocatorRole NVARCHAR(500);
    PRINT 'Added AllocatorRole';
END
ELSE
BEGIN
    ALTER TABLE ClientRequests ALTER COLUMN AllocatorRole NVARCHAR(500);
    PRINT 'Altered AllocatorRole to NVARCHAR(500)';
END
GO

PRINT 'AllocatorRole column ready.';
