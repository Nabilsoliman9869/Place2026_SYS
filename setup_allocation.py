import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def setup_allocation():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    # 1. Create Matches Table
    print("\n--- Checking/Creating Matches Table ---")
    try:
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Matches' AND xtype='U')
            CREATE TABLE Matches (
                MatchID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT,
                RequestID INT,
                Status NVARCHAR(50), -- Proposed, Approved, Interview Scheduled, Hired, Rejected
                AllocatorID INT,
                MatchDate DATETIME DEFAULT GETDATE(),
                InterviewDate DATETIME,
                InterviewNotes NVARCHAR(MAX),
                ReviewNotes NVARCHAR(MAX)
            )
        """)
        conn.commit()
        print("Matches table ensured.")
    except Exception as e:
        print(f"Error creating Matches table: {e}")

    # 2. Inspect ClientRequests
    print("\n--- ClientRequests Columns ---")
    try:
        cursor.execute("SELECT TOP 1 * FROM ClientRequests")
        columns = [column[0] for column in cursor.description]
        print(columns)
    except Exception as e:
        print(f"Error inspecting ClientRequests: {e}")

    # 3. Check for Allocator Role
    print("\n--- Check Allocator Users ---")
    try:
        cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Role IN ('Allocator', 'Allocation_Specialist', 'Manager')")
        for r in cursor.fetchall():
            print(r)
    except:
        pass

    conn.close()

if __name__ == '__main__':
    setup_allocation()
