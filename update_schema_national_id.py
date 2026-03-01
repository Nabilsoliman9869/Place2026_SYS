import pyodbc
import json

def get_db_connection():
    with open('db_config.json', 'r') as f:
        config = json.load(f)
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['server']},{config['port']};DATABASE={config['database']};UID={config['username']};PWD={config['password']}"
    return pyodbc.connect(conn_str)

def add_national_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("Adding NationalID column...")
        cursor.execute("IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'NationalID' AND Object_ID = Object_ID(N'Candidates')) ALTER TABLE Candidates ADD NationalID NVARCHAR(50)")
        print("✅ NationalID added.")
        conn.commit()
    except Exception as e:
        print(f"❌ Error: {e}")
    conn.close()

if __name__ == "__main__":
    add_national_id()
