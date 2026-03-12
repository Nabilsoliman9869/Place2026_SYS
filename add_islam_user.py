#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""إضافة مستخدم islam إلى جدول Users_1 (كلمة المرور: 123456)"""
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("ملف db_config.json غير موجود. قم بإعداد الاتصال أولاً من /setup")
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    cfg = load_config()
    if not cfg:
        return
    try:
        import pyodbc
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={cfg.get('server', '.')},{cfg.get('port', '1433')};"
            f"DATABASE={cfg.get('database', 'Place2026DB')};"
            f"UID={cfg.get('username', 'sa')};"
            f"PWD={cfg.get('password', '')};"
            f"TrustServerCertificate=Yes;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Username FROM Users_1 WHERE LOWER(RTRIM(Username)) = 'islam'")
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE Users_1 SET Password = ? WHERE UserID = ?", ('123456', row[0]))
            conn.commit()
            print(f"تم تحديث كلمة مرور islam إلى 123456 (UserID={row[0]})")
        else:
            cursor.execute(
                "INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?, ?, ?, ?)",
                ('islam', '123456', 'Manager', 'إسلام')
            )
            conn.commit()
            print("تم إضافة المستخدم islam بكلمة المرور 123456")
        conn.close()
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == '__main__':
    main()
