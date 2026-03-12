-- جدول مفضّلات التدفق النقدي (قبض / صرف) — صف واحد لكل مستخدم
-- منقول من Nuit Cosmetics للمحاسب إسلام
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CashflowUserConfig')
BEGIN
    CREATE TABLE dbo.CashflowUserConfig (
        UserId   NVARCHAR(128) NOT NULL PRIMARY KEY,
        ConfigJson NVARCHAR(MAX) NULL,
        UpdatedAt DATETIME2 NULL DEFAULT GETDATE()
    );
END
GO
