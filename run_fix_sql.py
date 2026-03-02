"""
تشغيل fix_all_tables_and_columns.sql على قاعدة البيانات باستخدام db_config.json
شغّل من مجلد المشروع: python run_fix_sql.py
"""
import os
import sys
import json
import pyodbc

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base, 'db_config.json')
    sql_path = os.path.join(base, 'fix_all_tables_and_columns.sql')

    if not os.path.exists(config_path):
        print('لا يوجد db_config.json — لا أستطيع الاتصال بقاعدة البيانات.')
        print('ضع ملف الإعدادات أو شغّل fix_all_tables_and_columns.sql يدوياً من SSMS.')
        sys.exit(1)
    if not os.path.exists(sql_path):
        print('لا يوجد fix_all_tables_and_columns.sql في مجلد المشروع.')
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    server = config.get('server', '.')
    port = config.get('port', '1433')
    database = config.get('database', 'Place2026DB')
    username = config.get('username', '')
    password = config.get('password', '')
    use_trusted = config.get('use_trusted', False)

    if use_trusted:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};'

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # إزالة أسطر USE و GO (تعليق أو نصوص فقط) حتى لا تسبب خطأ في pyodbc
    lines = []
    for line in sql.splitlines():
        s = line.strip()
        if s.startswith('--') or s.upper() == 'GO':
            continue
        if s.upper().startswith('USE ') and s.endswith(';'):
            continue
        lines.append(line)
    sql = '\n'.join(lines)

    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql)
        print('تم تنفيذ تصحيح الجداول والأعمدة بنجاح.')
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print('خطأ في الاتصال أو تنفيذ SQL:', e)
        sys.exit(1)

if __name__ == '__main__':
    main()
