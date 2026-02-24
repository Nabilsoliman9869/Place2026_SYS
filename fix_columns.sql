-- Fix Missing Columns Script

-- Add CreatedAt to Clients if missing
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Clients'))
BEGIN
    ALTER TABLE Clients ADD CreatedAt DATETIME DEFAULT GETDATE();
END
GO

-- Add CreatedAt to ClientRequests if missing
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'ClientRequests'))
BEGIN
    ALTER TABLE ClientRequests ADD CreatedAt DATETIME DEFAULT GETDATE();
END
GO

-- Add CreatedAt to Campaigns if missing
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Campaigns'))
BEGIN
    ALTER TABLE Campaigns ADD CreatedAt DATETIME DEFAULT GETDATE();
END
GO

-- Add CreatedAt to Candidates if missing
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'CreatedAt' AND Object_ID = Object_ID(N'Candidates'))
BEGIN
    ALTER TABLE Candidates ADD CreatedAt DATETIME DEFAULT GETDATE();
END
GO
