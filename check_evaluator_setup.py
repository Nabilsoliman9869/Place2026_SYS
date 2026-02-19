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
        
        # 1. Check for 'Evaluations' Table
        cursor.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Evaluations'")
        if not cursor.fetchone():
            print("Creating Evaluations table...")
            cursor.execute("""
                CREATE TABLE Evaluations (
                    EvaluationID INT PRIMARY KEY IDENTITY(1,1),
                    CandidateID INT NOT NULL,
                    SlotID INT,
                    Score_Comprehension INT DEFAULT 0,
                    Score_Fluency INT DEFAULT 0,
                    Score_Pronunciation INT DEFAULT 0,
                    Score_Structure INT DEFAULT 0,
                    Score_Vocabulary INT DEFAULT 0,
                    CEFR_Level VARCHAR(50),
                    Decision VARCHAR(50),
                    RecommendedLevel VARCHAR(50),
                    Comments NVARCHAR(MAX),
                    EvaluatorID INT,
                    EvaluationType VARCHAR(50),
                    RecordingLink NVARCHAR(MAX),
                    CreatedAt DATETIME DEFAULT GETDATE()
                )
            """)
            print("Evaluations table created.")
        
        # 2. Check for Evaluator User
        cursor.execute("SELECT UserID FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment')")
        if not cursor.fetchone():
            print("Creating Talent Evaluator user...")
            # Role: Talent (or Talent_Recruitment) is used for conducting tests/evaluations in app.py logic
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role) VALUES ('tal_eval', '123', 'Talent_Recruitment')")
            print("User 'tal_eval' created.")
        else:
            print("Talent Evaluator user already exists.")

        conn.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    main()
