IF NOT EXISTS (SELECT * FROM Users WHERE Username = 'trainer1')
BEGIN
    INSERT INTO Users (Username, Password, Role, FullName, Email)
    VALUES ('trainer1', '123456', 'Trainer', 'Master Trainer', 'trainer@place2026.com');
END
GO
