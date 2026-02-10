import pyodbc
import json
import os
import datetime

# Configuration
CONFIG_FILE = 'db_config.json'
OUTPUT_FILE = 'data_export.sql'

def get_connection():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    else:
        config = {"server": ".", "port": "1433", "database": "Place2026DB", "use_trusted": True}

    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={config.get("username")};PWD={config.get("password")}'
    
    return pyodbc.connect(conn_str)

def format_value(val):
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, datetime.datetime) or isinstance(val, datetime.date):
        return f"'{val}'"
    # Escape single quotes in strings
    return f"'{str(val).replace("'", "''")}'"

def generate_data_script():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get list of user tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("-- Database Data Export\n")
            f.write("-- Run this AFTER creating tables\n\n")
            
            for table in tables:
                print(f"Exporting data for: {table}")
                
                # Check for Identity Column
                has_identity = False
                cursor.execute(f"SELECT COUNT(*) FROM sys.identity_columns WHERE object_id = OBJECT_ID('{table}')")
                if cursor.fetchone()[0] > 0:
                    has_identity = True
                
                # Fetch Data
                cursor.execute(f"SELECT * FROM [{table}]")
                rows = cursor.fetchall()
                
                if not rows:
                    continue
                    
                columns = [column[0] for column in cursor.description]
                cols_str = ", ".join([f"[{c}]" for c in columns])
                
                if has_identity:
                    f.write(f"SET IDENTITY_INSERT [{table}] ON;\n")
                
                for row in rows:
                    vals = [format_value(v) for v in row]
                    vals_str = ", ".join(vals)
                    f.write(f"INSERT INTO [{table}] ({cols_str}) VALUES ({vals_str});\n")
                
                if has_identity:
                    f.write(f"SET IDENTITY_INSERT [{table}] OFF;\n")
                
                f.write("GO\n\n")
                
        print(f"Data export completed: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_data_script()
