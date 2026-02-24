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

def check_habiba():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for 'habiba' (case insensitive usually in SQL Server, but using LIKE to be sure)
        cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Username LIKE ?", ('%habiba%',))
        users = cursor.fetchall()
        
        if users:
            print("--- Found Users matching 'habiba' ---")
            for u in users:
                print(f"ID: {u[0]}, Username: {u[1]}, Role: {u[2]}")
        else:
            print("No user found with name like 'habiba'.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    check_habiba()
