import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def update_schema():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    cursor = conn.cursor()
    
    print(">>> Creating Unified 'Schedules' Table...")

    try:
        # 1. Create Table if not exists
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Schedules' AND xtype='U')
            CREATE TABLE Schedules (
                ScheduleID INT IDENTITY(1,1) PRIMARY KEY,
                
                -- Context: 'Talent_Recruitment', 'Talent_Training', 'Client_Interview', 'General'
                Context NVARCHAR(50) NOT NULL, 
                
                -- Ownership (Polymorphic-ish)
                OwnerUserID INT NULL, -- For Staff (Talent, Trainers, etc.)
                OwnerClientID INT NULL, -- For Corporate Clients (Interview Slots)
                
                -- Time Slot
                SlotDate DATE NOT NULL,
                SlotTime NVARCHAR(10) NOT NULL, -- HH:MM
                
                -- Status & Booking
                Status NVARCHAR(50) DEFAULT 'Available', -- Available, Booked, Blocked, Completed, NoShow
                BookedCandidateID INT NULL,
                
                -- Metadata
                BookingMode NVARCHAR(50), -- Phone, Online, InPerson
                MeetingLink NVARCHAR(MAX), -- Zoom/Teams Link
                Notes NVARCHAR(MAX),
                
                CreatedAt DATETIME DEFAULT GETDATE(),
                
                -- Constraints
                FOREIGN KEY (OwnerUserID) REFERENCES Users_1(UserID),
                FOREIGN KEY (OwnerClientID) REFERENCES Clients(ClientID),
                FOREIGN KEY (BookedCandidateID) REFERENCES Candidates(CandidateID)
            )
        """)
        print("Table 'Schedules' Created/Verified.")

        # 2. Migrate Data from TASchedules (if any)
        print("Migrating data from TASchedules...")
        cursor.execute("SELECT COUNT(*) FROM TASchedules")
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Migrate only if Schedules is empty to avoid double migration
            cursor.execute("SELECT COUNT(*) FROM Schedules WHERE Context='Talent_Recruitment'")
            existing = cursor.fetchone()[0]
            
            if existing == 0:
                print(f"Migrating {count} slots from TASchedules...")
                cursor.execute("""
                    INSERT INTO Schedules (Context, OwnerUserID, SlotDate, SlotTime, Status, BookedCandidateID)
                    SELECT 
                        'Talent_Recruitment', 
                        EvaluatorID, 
                        SlotDate, 
                        SlotTime, 
                        Status, 
                        CandidateID
                    FROM TASchedules
                """)
                print("Migration Complete.")
            else:
                print("Data already migrated or Schedules table not empty. Skipping migration.")
        
        conn.commit()
        print(">>> Unified Schema Setup Complete.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    update_schema()
