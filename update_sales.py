import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def update_sales_structure():
    print("--- UPDATING SALES STRUCTURE ---")
    if not os.path.exists(CONFIG_FILE): return

    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    username = config.get("username", "")
    password = config.get("password", "")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 1. Create Services Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Services' AND xtype='U')
            CREATE TABLE Services (
                ServiceID INT IDENTITY(1,1) PRIMARY KEY,
                ServiceName NVARCHAR(100) NOT NULL,
                DefaultPrice DECIMAL(18, 2) DEFAULT 0
            )
        """)
        
        # 2. Populate Services
        services = [
            (u'اختبار تحديد مستوى', 0),
            (u'اختبار سمات شخصية', 0),
            (u'اختبار hr كامل', 0),
            (u'اختبارات مهنية', 0),
            (u'اختبارت اكاديمية', 0),
            (u'اختبارات اخرى', 0),
            (u'تصميم سيرة ذاتية وبروفايل', 0),
            (u'عمل فيديو سي في Video Cv', 0),
            (u'خدمات اخرى', 0)
        ]
        
        for svc in services:
            cursor.execute("SELECT ServiceID FROM Services WHERE ServiceName=?", (svc[0],))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Services (ServiceName, DefaultPrice) VALUES (?,?)", svc)
                print(f"Added Service: {svc[0]}")

        # 3. Ensure 'Cash Client' exists in Candidates
        cursor.execute("SELECT CandidateID FROM Candidates WHERE FullName = ?", (u'عميل نقدي',))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Candidates (FullName, Phone, Status, InterestLevel) VALUES (?, ?, 'Customer', 'Low')", (u'عميل نقدي', '0000000000'))
            print("Added 'Cash Client' to Candidates.")
            
        # 4. Update GeneralSales Table to link to CandidateID (Optional but good)
        try:
            cursor.execute("ALTER TABLE GeneralSales ADD CandidateID INT")
            print("Added CandidateID to GeneralSales.")
        except: pass # Probably exists
        
        conn.commit()
        print(">>> SALES STRUCTURE UPDATED <<<")
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_sales_structure()
