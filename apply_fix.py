import pyodbc
import json
import os

CONFIG_FILE = r'E:\Place _trae\db_config.json'
SCHEMA_FILE = r'E:\Place_2026_SYS\fix_columns.sql'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def run_fix():
    config = load_config()
    if not config: return

    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        with open(SCHEMA_FILE, 'r') as f:
            commands = f.read().replace('\r\n', '\n').split('GO\n')
            
        for cmd in commands:
            if cmd.strip():
                try:
                    cursor.execute(cmd)
                    conn.commit()
                    print("Executed command successfully.")
                except Exception as e:
                    print(f"Error executing command: {e}")
                    
        print("Fix script completed.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_fix()
