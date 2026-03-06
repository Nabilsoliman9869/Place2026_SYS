"""
إضافة مستخدمي التدريب (منسق، مدرب، إلخ) إلى Users_1 إن لم يكونوا موجودين.
شغّل مرة واحدة: python add_training_users.py
"""
import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def main():
    if not os.path.exists(CONFIG_FILE):
        print("لا يوجد db_config.json")
        return
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    server = config.get('server', '.')
    port = config.get('port', '1433')
    database = config.get('database', 'Place2026DB')
    username = config.get('username', 'sa')
    password = config.get('password', '')
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
    conn = pyodbc.connect(conn_str)
    conn.autocommit = False
    cursor = conn.cursor()

    users = [
        ('train_mgr', '123', 'TrainingManager', 'مدير التدريب'),
        ('train_head', '123', 'TrainingHead', 'رئيس قسم التدريب'),
        ('train_lead', '123', 'TrainingLead', 'قائد التدريب'),
        ('train_coord', '123', 'TrainingCoordinator', 'منسق التدريب'),
        ('train_sales', '123', 'TrainingSales', 'مبيعات التدريب'),
        ('ta_train', '123', 'Talent_Training', 'مختبر مواهب التدريب'),
        ('trainer1', '123', 'Trainer', 'مدرب'),
    ]
    added = 0
    for u in users:
        cursor.execute("SELECT UserID FROM Users_1 WHERE Username = ?", (u[0],))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, ?, ?, ?)",
                u
            )
            print(f"تمت إضافة: {u[0]} ({u[2]})")
            added += 1
        else:
            print(f"موجود مسبقاً: {u[0]}")
    conn.commit()
    conn.close()
    print(f"\nانتهى. تم إضافة {added} مستخدم.")

if __name__ == '__main__':
    main()
