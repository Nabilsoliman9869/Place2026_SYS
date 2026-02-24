import pyodbc
import json
import os
import time

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};'
    if config.get("use_trusted"):
        conn_str += 'Trusted_Connection=yes;'
    else:
        conn_str += f'UID={config.get("username", "")};PWD={config.get("password", "")}'
    
    return pyodbc.connect(conn_str)

def verify_and_update_schema():
    print(">>> STARTING MASTER SCHEMA VERIFICATION <<<")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Define Tables and their Columns (Name, Type)
        schema_def = {
            "Users_1": [
                ("UserID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("Username", "NVARCHAR(100)"),
                ("Password", "NVARCHAR(100)"),
                ("Role", "NVARCHAR(50)")
            ],
            "Candidates": [
                ("CandidateID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("FullName", "NVARCHAR(200)"),
                ("Phone", "NVARCHAR(50)"),
                ("Email", "NVARCHAR(150)"),
                ("Nationality", "NVARCHAR(50)"),
                ("GraduationStatus", "NVARCHAR(50)"),
                ("SourceChannel", "NVARCHAR(50)"),
                ("Status", "NVARCHAR(50)"),
                ("CreatedAt", "DATETIME DEFAULT GETDATE()"),
                ("SalesAgentID", "INT"),
                ("CampaignID", "INT"),
                ("PrimaryIntent", "NVARCHAR(50)"),
                ("CurrentCEFR", "NVARCHAR(20)"),
                ("WorkStatus", "NVARCHAR(100)"),
                ("Venue", "NVARCHAR(50)"),
                ("PlacementReason", "NVARCHAR(100)"),
                ("MarketingAssessment", "NVARCHAR(MAX)"),
                ("PreviousApplicationDate", "DATETIME"),
                ("AvailabilityStatus", "NVARCHAR(50)"),
                ("RecruiterID", "INT"),
                ("AllocatorID", "INT")
            ],
            "Campaigns": [
                ("CampaignID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("Name", "NVARCHAR(150)"),
                ("Platform", "NVARCHAR(50)"),
                ("Budget", "DECIMAL(10,2)"),
                ("Status", "NVARCHAR(50)"),
                ("RequestID", "INT"),
                ("MediaChannel", "NVARCHAR(50)"),
                ("AdText", "NVARCHAR(MAX)"),
                ("StartDate", "DATE"),
                ("EndDate", "DATE"),
                ("Type", "NVARCHAR(50)")
            ],
            "TASchedules": [
                ("SlotID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("SlotDate", "DATE"),
                ("SlotTime", "NVARCHAR(10)"),
                ("Status", "NVARCHAR(50)"),
                ("EvaluatorID", "INT"),
                ("CandidateID", "INT"),
                ("BookedBy", "INT"),
                ("Type", "NVARCHAR(50)"),
                ("InterviewType", "NVARCHAR(50)")
            ],
            "Clients": [
                ("ClientID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("CompanyName", "NVARCHAR(150)"),
                ("Industry", "NVARCHAR(100)"),
                ("ContactPerson", "NVARCHAR(100)"),
                ("Email", "NVARCHAR(100)"),
                ("Phone", "NVARCHAR(50)"),
                ("Address", "NVARCHAR(MAX)"),
                ("CreatedAt", "DATETIME DEFAULT GETDATE()")
            ],
            "ClientRequests": [
                ("RequestID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("ClientID", "INT"),
                ("JobTitle", "NVARCHAR(150)"),
                ("NeededCount", "INT"),
                ("Status", "NVARCHAR(50)"),
                ("EnglishLevel", "NVARCHAR(50)"),
                ("SalaryFrom", "DECIMAL(10,2)"),
                ("SalaryTo", "DECIMAL(10,2)"),
                ("Requirements", "NVARCHAR(MAX)"),
                ("PreferredNationality", "NVARCHAR(50)"),
                ("SupplyType", "NVARCHAR(50)"),
                ("Benefits", "NVARCHAR(MAX)"),
                ("TechnicalSkills", "NVARCHAR(MAX)"),
                ("Insurance", "NVARCHAR(50)"),
                ("AgeFrom", "INT"),
                ("AgeTo", "INT"),
                ("Gender", "NVARCHAR(20)"),
                ("Location", "NVARCHAR(100)"),
                ("RequestDate", "DATETIME DEFAULT GETDATE()")
            ],
             "RecruitmentFailures": [
                ("ID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("CandidateID", "INT"),
                ("Stage", "NVARCHAR(50)"),
                ("Reason", "NVARCHAR(MAX)"),
                ("LoggedBy", "INT"),
                ("CreatedAt", "DATETIME DEFAULT GETDATE()")
            ],
            "Notifications": [
                ("NotificationID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("UserID", "INT"),
                ("Message", "NVARCHAR(MAX)"),
                ("Type", "NVARCHAR(50)"),
                ("RelatedID", "INT"),
                ("IsRead", "BIT DEFAULT 0"),
                ("CreatedAt", "DATETIME DEFAULT GETDATE()")
            ],
             "Services": [
                ("ServiceID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("ServiceName", "NVARCHAR(100)"),
                ("Price", "DECIMAL(10,2)"),
                ("Category", "NVARCHAR(50)")
            ],
             "GeneralSales": [
                ("SaleID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("CandidateID", "INT"),
                ("ServiceID", "INT"),
                ("Amount", "DECIMAL(10,2)"),
                ("SaleDate", "DATETIME DEFAULT GETDATE()"),
                ("CreatedBy", "INT")
            ],
             "InvoiceHeaders": [
                ("InvoiceID", "INT IDENTITY(1,1) PRIMARY KEY"),
                ("CandidateID", "INT"),
                ("TotalAmount", "DECIMAL(10,2)"),
                ("Status", "NVARCHAR(50)"),
                ("CreatedAt", "DATETIME DEFAULT GETDATE()")
             ]
        }

        # 2. Iterate and Check/Create
        for table, columns in schema_def.items():
            # Check if table exists
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"Creating Table: {table}")
                # Simple create with first col (Primary Key usually)
                pk_col, pk_type = columns[0]
                cursor.execute(f"CREATE TABLE {table} ({pk_col} {pk_type})")
                conn.commit()

            # Check columns
            for col_name, col_type in columns:
                cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table}' AND COLUMN_NAME='{col_name}'")
                if cursor.fetchone()[0] == 0:
                    print(f"  + Adding Column: {table}.{col_name}")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD {col_name} {col_type}")
                        conn.commit()
                    except Exception as e:
                        print(f"    ! Error adding {col_name}: {e}")
        
        print(">>> MASTER SCHEMA VERIFICATION COMPLETED SUCCESSFULLY. <<<")
        conn.close()
        return True

    except Exception as e:
        print(f"!!! CRITICAL SCHEMA ERROR: {e}")
        return False

if __name__ == '__main__':
    verify_and_update_schema()
