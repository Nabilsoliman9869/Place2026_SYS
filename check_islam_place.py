#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""التحقق من مستخدم islam في جدول Users_1 (Place 2026)"""
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')

def main():
    if not os.path.exists(CONFIG_FILE):
        print("ملف db_config.json غير موجود. قم بإعداد الاتصال من /setup أولاً.")
        return
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
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
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UserID, Username, Password, Role, FullName 
            FROM Users_1 
            WHERE LOWER(RTRIM(Username)) LIKE '%islam%'
        """)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        if not rows:
            print("--- لا يوجد مستخدم باسم islam في Users_1 ---")
            print("\nجميع المستخدمين الحاليين:")
            conn = pyodbc.connect(conn_str, timeout=5)
            cur = conn.cursor()
            cur.execute("SELECT UserID, Username, Role FROM Users_1 ORDER BY UserID")
            for r in cur.fetchall():
                print(f"  UserID={r[0]}, Username='{r[1]}', Role={r[2]}")
            conn.close()
            return
        print(f"--- عدد النتائج: {len(rows)} ---")
        for r in rows:
            d = dict(zip(cols, r))
            print(f"\nUserID: {d.get('UserID')}")
            print(f"Username: {d.get('Username')!r}")
            print(f"Password: {d.get('Password')!r}")
            print(f"Role: {d.get('Role')}")
            print(f"FullName: {d.get('FullName')}")
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == '__main__':
    main()
