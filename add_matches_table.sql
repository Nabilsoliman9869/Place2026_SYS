-- Add Matches Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Matches' AND xtype='U')
BEGIN
    CREATE TABLE Matches (
        MatchID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
        RequestID INT FOREIGN KEY REFERENCES ClientRequests(RequestID),
        MatchDate DATETIME DEFAULT GETDATE(),
        Status NVARCHAR(50) DEFAULT 'Proposed', -- Proposed, Interviewing, Accepted, Rejected
        Notes NVARCHAR(MAX)
    );
END
GO
