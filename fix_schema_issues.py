import pyodbc
import json

def get_db_connection():
    with open('db_config.json', 'r') as f:
        config = json.load(f)
    
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['server']},{config['port']};DATABASE={config['database']};UID={config['username']};PWD={config['password']}"
    return pyodbc.connect(conn_str)

def fix_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Checking Candidates table schema...")
    
    try:
        # 1. Fix Language Level Column Size (Image 3 Fix)
        print("Altering CurrentCEFR to NVARCHAR(100)...")
        cursor.execute("ALTER TABLE Candidates ALTER COLUMN CurrentCEFR NVARCHAR(100)")
        print("✅ CurrentCEFR resized.")
    except Exception as e:
        print(f"⚠️ CurrentCEFR resize failed (might already be large enough): {e}")

    try:
        # 2. Add 'HasWorkExperience' column (Image 1 Fix)
        # Check if exists first
        cursor.execute("SELECT COUNT(*) FROM sys.columns WHERE Name = N'HasWorkExperience' AND Object_ID = Object_ID(N'Candidates')")
        if cursor.fetchone()[0] == 0:
            print("Adding HasWorkExperience column...")
            cursor.execute("ALTER TABLE Candidates ADD HasWorkExperience BIT DEFAULT 0")
            print("✅ HasWorkExperience added.")
        else:
            print("ℹ️ HasWorkExperience already exists.")
            
    except Exception as e:
        print(f"❌ Failed to add HasWorkExperience: {e}")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    fix_schema()
