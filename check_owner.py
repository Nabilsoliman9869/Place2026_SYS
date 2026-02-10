import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def check_booked_owner():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    print("\n--- Latest Booked Schedule ---")
    # Fetch the most recently booked slot
    cursor.execute("""
        SELECT TOP 1 S.ScheduleID, S.SlotDate, S.SlotTime, S.OwnerUserID, U.Username, S.Context
        FROM Schedules S 
        LEFT JOIN Users_1 U ON S.OwnerUserID = U.UserID 
        WHERE S.Status='Booked' 
        ORDER BY S.ScheduleID DESC
    """)
    row = cursor.fetchone()
    
    if row:
        print(f"ScheduleID: {row.ScheduleID}")
        print(f"Date/Time: {row.SlotDate} {row.SlotTime}")
        print(f"OwnerUserID: {row.OwnerUserID} ({row.Username if row.Username else 'NULL/Any'})")
        print(f"Context: {row.Context}")
        
        if row.OwnerUserID:
            print(f"\n>>> This test appears ONLY to user: {row.Username} (ID: {row.OwnerUserID})")
        else:
            print("\n>>> This test appears to ALL Talent users (Shared Pool).")
    else:
        print("No booked schedules found.")

    conn.close()

if __name__ == '__main__':
    check_booked_owner()
