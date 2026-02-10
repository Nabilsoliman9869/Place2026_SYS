import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place_2026_SYS\db_config.json'

def upgrade_candidates_table():
    print("Upgrading Candidates Table Schema...")
    if not os.path.exists(CONFIG_FILE): return
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Add InterestLevel
        try:
            cursor.execute("ALTER TABLE Candidates ADD InterestLevel NVARCHAR(50)")
            print("Added InterestLevel column.")
        except: print("InterestLevel might exist.")
        
        # Add Feedback
        try:
            cursor.execute("ALTER TABLE Candidates ADD Feedback NVARCHAR(MAX)")
            print("Added Feedback column.")
        except: print("Feedback might exist.")
        
        # Add NextFollowUpDate
        try:
            cursor.execute("ALTER TABLE Candidates ADD NextFollowUpDate DATE")
            print("Added NextFollowUpDate column.")
        except: print("NextFollowUpDate might exist.")

        # Add CampaignID if missing
        try:
            cursor.execute("ALTER TABLE Candidates ADD CampaignID INT")
            print("Added CampaignID column.")
        except: print("CampaignID might exist.")
        
        # Add SoftSkills/EnglishLevel/IsReadyForMatching (Just in case)
        try: cursor.execute("ALTER TABLE Candidates ADD SoftSkills NVARCHAR(MAX)"); print("Added SoftSkills"); except: pass
        try: cursor.execute("ALTER TABLE Candidates ADD EnglishLevel NVARCHAR(50)"); print("Added EnglishLevel"); except: pass
        try: cursor.execute("ALTER TABLE Candidates ADD IsReadyForMatching BIT DEFAULT 0"); print("Added IsReadyForMatching"); except: pass

        conn.commit()
        print(">>> SUCCESS: Candidates Table Upgraded <<<")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    upgrade_candidates_table()
