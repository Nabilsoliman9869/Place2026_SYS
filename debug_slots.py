import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def debug_slots():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return

    cursor = conn.cursor()
    
    print("\n--- Users (Adel & TA001) ---")
    cursor.execute("SELECT UserID, Username, Role FROM Users_1 WHERE Username IN ('adel', 'ta001')")
    for r in cursor.fetchall():
        print(f"ID: {r.UserID}, User: {r.Username}, Role: {r.Role}")

    print("\n--- Booked Slots in Schedules ---")
    cursor.execute("""
        SELECT S.ScheduleID, S.SlotDate, S.SlotTime, S.Status, S.OwnerUserID, U.Username as OwnerName, S.BookedCandidateID
        FROM Schedules S
        LEFT JOIN Users_1 U ON S.OwnerUserID = U.UserID
        WHERE S.Status = 'Booked'
    """)
    rows = cursor.fetchall()
    if not rows:
        print("No Booked slots found.")
    for r in rows:
        print(f"Slot {r.ScheduleID}: {r.SlotDate} {r.SlotTime} | OwnerID: {r.OwnerUserID} ({r.OwnerName}) | Candidate: {r.BookedCandidateID}")

    conn.close()

if __name__ == '__main__':
    debug_slots()
