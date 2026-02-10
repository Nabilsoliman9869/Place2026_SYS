import pyodbc
import json
import os
from datetime import datetime, timedelta

CONFIG_FILE = 'db_config.json'

def get_db_connection():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]},{config["port"]};DATABASE={config["database"]};UID={config["username"]};PWD={config["password"]}'
    return pyodbc.connect(conn_str)

def generate_slots(context='Talent_Recruitment'):
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    cursor = conn.cursor()

    # 1. Get Talent Evaluators based on Context
    role_filter = "('Talent', 'Talent_Recruitment')" if context == 'Talent_Recruitment' else "('Talent', 'Talent_Training')"
    
    print(f">>> Generating Slots for Context: {context}")
    cursor.execute(f"SELECT UserID FROM Users_1 WHERE Role IN {role_filter}")
    talent_users = [row[0] for row in cursor.fetchall()]
    
    if not talent_users:
        print(f"No specific users found for {context}. Slots will be unassigned (Open Pool).")
        talent_users = [None] 

    # 2. Define Range (Next 14 Days)
    start_date = datetime.today()
    days_to_generate = 14
    
    # Schedule: 10 AM to 10 PM (22:00)
    start_hour = 10
    end_hour = 22
    
    print(f"Generating slots from {start_date.date()} for {days_to_generate} days...")
    print("Schedule: 10:00 to 22:00, 15 min intervals. Excludes Fri & Sat.")

    slots_created = 0

    for day_offset in range(days_to_generate):
        current_date = start_date + timedelta(days=day_offset)
        
        # Check Weekend (Fri=4, Sat=5)
        if current_date.weekday() in [4, 5]:
            # print(f"Skipping {current_date.date()} (Weekend)")
            continue
            
        date_str = current_date.strftime('%Y-%m-%d')
        
        day_slots = []
        for h in range(start_hour, end_hour): 
            for m in [0, 15, 30, 45]:
                time_str = f"{h:02d}:{m:02d}"
                
                for uid in talent_users:
                    day_slots.append((context, date_str, time_str, 'Available', uid))

        # Insert batch for the day
        for slot in day_slots:
            try:
                # Check exist in Schedules (Unified Table)
                check_sql = "SELECT ScheduleID FROM Schedules WHERE Context=? AND SlotDate=? AND SlotTime=?"
                check_params = [slot[0], slot[1], slot[2]]
                if slot[4]: # If EvaluatorID (OwnerUserID) is specific
                    check_sql += " AND OwnerUserID=?"
                    check_params.append(slot[4])
                else:
                    check_sql += " AND OwnerUserID IS NULL"
                
                cursor.execute(check_sql, check_params)
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO Schedules (Context, SlotDate, SlotTime, Status, OwnerUserID) VALUES (?, ?, ?, ?, ?)", slot)
                    slots_created += 1
            except Exception as e:
                print(f"Error inserting slot {slot}: {e}")
        
        conn.commit()
        # print(f"Processed {date_str}...")

    print(f"Generation Complete for {context}. Created {slots_created} new slots.\n")
    conn.close()

if __name__ == "__main__":
    # Generate for Recruitment
    generate_slots('Talent_Recruitment')
    # Generate for Training
    generate_slots('Talent_Training')
