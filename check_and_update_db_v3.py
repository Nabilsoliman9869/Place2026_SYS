import pyodbc
import json

def get_db_connection():
    with open('db_config.json', 'r') as f:
        config = json.load(f)
    
    conn_str = (
        f"DRIVER={{{config['driver']}}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def column_exists(cursor, table, column):
    try:
        cursor.execute(f"SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND COLUMN_NAME = '{column}'")
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking column {column}: {e}")
        return False

def add_column_if_missing(cursor, table, column, type_def):
    if not column_exists(cursor, table, column):
        print(f"Adding column {column} to {table}...")
        try:
            cursor.execute(f"ALTER TABLE {table} ADD {column} {type_def}")
            print(f"Successfully added {column}.")
        except Exception as e:
            print(f"Failed to add {column}: {e}")
    else:
        print(f"Column {column} already exists in {table}.")

def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Update Candidates Table
        print("Checking Candidates Table...")
        add_column_if_missing(cursor, 'Candidates', 'Address', 'NVARCHAR(255)')
        add_column_if_missing(cursor, 'Candidates', 'Age', 'INT')
        add_column_if_missing(cursor, 'Candidates', 'WorkedHereBefore', 'BIT DEFAULT 0')
        add_column_if_missing(cursor, 'Candidates', 'PreviousApplicationDate', 'DATE')
        
        # 2. Update Matches Table
        print("\nChecking Matches Table...")
        add_column_if_missing(cursor, 'Matches', 'AllocatorFeedback', 'NVARCHAR(MAX)')
        
        conn.commit()
        print("\nDatabase check completed successfully.")
        
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
