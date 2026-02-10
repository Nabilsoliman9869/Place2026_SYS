import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def check_levels():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    print("\n--- Distinct Levels in Candidates (CurrentCEFR) ---")
    try:
        cursor.execute("SELECT DISTINCT CurrentCEFR FROM Candidates WHERE CurrentCEFR IS NOT NULL")
        for r in cursor.fetchall():
            print(f"'{r[0]}'")
    except Exception as e:
        print(f"Error querying Candidates: {e}")

    print("\n--- Distinct Levels in TrainingWaves (WaveName/Level?) ---")
    # Assuming TrainingWaves might have level info, or we look at Services?
    # Let's check table schema for TrainingWaves first
    try:
        cursor.execute("SELECT TOP 1 * FROM TrainingWaves")
        cols = [column[0] for column in cursor.description]
        print(f"TrainingWaves Columns: {cols}")
    except:
        print("TrainingWaves table not found or empty.")

    print("\n--- Distinct Levels in ClientRequests (EnglishLevel) ---")
    try:
        cursor.execute("SELECT DISTINCT EnglishLevel FROM ClientRequests WHERE EnglishLevel IS NOT NULL")
        for r in cursor.fetchall():
            print(f"'{r[0]}'")
    except:
        pass

    conn.close()

if __name__ == '__main__':
    check_levels()
