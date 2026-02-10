import pyodbc
import json
import os

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
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

def update_schema_and_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(">>> Starting Schema & Users Update...")

        # 1. Update ClientRequests Table (Nationality, SupplyType)
        print(">>> Updating ClientRequests Schema...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='ClientRequests' AND COLUMN_NAME='PreferredNationality')
            BEGIN
                ALTER TABLE ClientRequests ADD PreferredNationality NVARCHAR(50) DEFAULT 'Any';
                ALTER TABLE ClientRequests ADD SupplyType NVARCHAR(50) DEFAULT 'Full'; -- Full or Partial
            END
        """)

        # 2. Update Candidates Table (Legacy Data, SalesAgentID)
        print(">>> Updating Candidates Schema...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Candidates' AND COLUMN_NAME='LegacyData')
            BEGIN
                ALTER TABLE Candidates ADD LegacyData NVARCHAR(MAX); -- JSON or Text for old history
                ALTER TABLE Candidates ADD GraduationBatch NVARCHAR(100);
                ALTER TABLE Candidates ADD GraduationDate DATE;
                ALTER TABLE Candidates ADD SalesAgentID INT; -- Link to Users
            END
        """)

        # 3. Create Invoice Structure (Header & Body)
        print(">>> Creating Invoice Tables...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvoiceHeaders' AND xtype='U')
            CREATE TABLE InvoiceHeaders (
                InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
                ClientID INT, -- Can be NULL if individual
                CandidateID INT, -- Can be NULL if corporate
                InvoiceDate DATETIME DEFAULT GETDATE(),
                SubTotal FLOAT,
                DiscountType NVARCHAR(10), -- 'Percent' or 'Value'
                DiscountValue FLOAT DEFAULT 0,
                TaxPercent FLOAT DEFAULT 0,
                TotalAmount FLOAT,
                Status NVARCHAR(50) DEFAULT 'Unpaid',
                CreatedBy INT
            )

            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvoiceItems' AND xtype='U')
            CREATE TABLE InvoiceItems (
                ItemID INT IDENTITY(1,1) PRIMARY KEY,
                InvoiceID INT FOREIGN KEY REFERENCES InvoiceHeaders(InvoiceID),
                Description NVARCHAR(200),
                Quantity INT DEFAULT 1,
                UnitPrice FLOAT,
                LineTotal FLOAT
            )
        """)

        # 4. Create Users (Talent, TrainingHead, TrainingManager, Trainer)
        print(">>> Creating/Updating Users...")
        users = [
            ('talent', '123', 'Talent'),
            ('train_head', '123', 'TrainingHead'),
            ('train_mgr', '123', 'TrainingManager'),
            ('trainer1', '123', 'Trainer'),
            ('sales1', '123', 'Sales') # Ensure we have a sales user for linking
        ]

        for u, p, r in users:
            # Check if user exists
            cursor.execute("SELECT Count(*) FROM Users_1 WHERE Username=?", (u,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role) VALUES (?, ?, ?)", (u, p, r))
                print(f"Created user: {u} ({r})")
            else:
                # Update role just in case
                cursor.execute("UPDATE Users_1 SET Role=? WHERE Username=?", (r, u))
                print(f"Updated user: {u} ({r})")

        conn.commit()
        print(">>> All Updates Completed Successfully.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    update_schema_and_users()
