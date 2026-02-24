import pyodbc
import json

def get_db_connection():
    with open('db_config.json', 'r') as f:
        config = json.load(f)
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={config['server']},{config['port']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("--- Evaluators Count ---")
        
        # 1. Talent Recruitment Evaluators (للتوظيف)
        cursor.execute("SELECT COUNT(*) FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment')")
        rec_count = cursor.fetchone()[0]
        print(f"Recruitment Evaluators (Talent): {rec_count}")
        
        cursor.execute("SELECT Username FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment')")
        users = cursor.fetchall()
        for u in users:
            print(f" - {u[0]}")

        # 2. Training Evaluators (للتدريب - Placement Tests)
        # Assuming role 'TA-Training' or 'Trainer' handles placement tests for Academy
        cursor.execute("SELECT COUNT(*) FROM Users_1 WHERE Role IN ('TA-Training', 'Trainer')")
        train_count = cursor.fetchone()[0]
        print(f"\nTraining Evaluators (Trainers/TA): {train_count}")
        
        cursor.execute("SELECT Username FROM Users_1 WHERE Role IN ('TA-Training', 'Trainer')")
        users = cursor.fetchall()
        for u in users:
            print(f" - {u[0]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    main()
