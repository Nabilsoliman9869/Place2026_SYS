
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
    
    # 1. Update Campaigns Table
    campaign_cols = [
        ("TargetCount", "INT"),
        ("LanguageLevel", "NVARCHAR(50)"),
        ("Nationality", "NVARCHAR(100)"),
        ("AgeFrom", "INT"),
        ("AgeTo", "INT"),
        ("PreferredLocation", "NVARCHAR(200)"),
        ("SpecialRequirements", "NVARCHAR(MAX)"),
        ("CreatedBy", "INT"),
        ("MediaType", "NVARCHAR(50)"),
        ("IsGraduated", "BIT")
    ]
    
    print("--- Updating Campaigns Table ---")
    for col, dtype in campaign_cols:
        try:
            cursor.execute(f"ALTER TABLE Campaigns ADD {col} {dtype}")
            print(f"Added {col} to Campaigns")
        except Exception as e:
            if "Column names in each table must be unique" in str(e):
                print(f"Column {col} already exists in Campaigns")
            else:
                print(f"Error adding {col}: {e}")

    # 2. Update Candidates Table
    candidate_cols = [
        ("EmploymentStatus", "NVARCHAR(50)"), # Unemployed, Employed, NoticePeriod
        ("IsReferredToTraining", "BIT DEFAULT 0"),
        ("RecruitmentStage", "NVARCHAR(50) DEFAULT 'New'"),
        ("RecruiterFeedback", "NVARCHAR(MAX)"),
        ("IsGraduated", "BIT") # True/False
    ]
    
    print("\n--- Updating Candidates Table ---")
    for col, dtype in candidate_cols:
        try:
            cursor.execute(f"ALTER TABLE Candidates ADD {col} {dtype}")
            print(f"Added {col} to Candidates")
        except Exception as e:
            if "Column names in each table must be unique" in str(e):
                print(f"Column {col} already exists in Candidates")
            else:
                print(f"Error adding {col}: {e}")

    # 3. Update Matches Table (For Interview Workflow)
    match_cols = [
        ("InterviewDate", "DATETIME"),
        ("InterviewNotes", "NVARCHAR(MAX)"),
        ("ClientFeedback", "NVARCHAR(MAX)")
    ]

    print("\n--- Updating Matches Table ---")
    for col, dtype in match_cols:
        try:
            cursor.execute(f"ALTER TABLE Matches ADD {col} {dtype}")
            print(f"Added {col} to Matches")
        except Exception as e:
            if "Column names in each table must be unique" in str(e):
                print(f"Column {col} already exists in Matches")
            else:
                print(f"Error adding {col}: {e}")

    conn.commit()
    conn.close()
    print("\n>>> Schema Update Complete <<<")

if __name__ == "__main__":
    update_schema()
