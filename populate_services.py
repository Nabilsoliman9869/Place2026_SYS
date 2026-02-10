import pyodbc
import json
import os

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

def populate_services():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Services")
        if cursor.fetchone()[0] == 0:
            services = [
                ('General English Course', 1500),
                ('Soft Skills Workshop', 500),
                ('CV Writing', 200),
                ('Career Consultation', 300),
                ('Placement Test', 100),
                ('HR Management Course', 2500),
                ('Digital Marketing', 2000)
            ]
            for s in services:
                cursor.execute("INSERT INTO Services (ServiceName, DefaultPrice) VALUES (?, ?)", s)
            print(f">>> Added {len(services)} default services.")
            conn.commit()
        else:
            print(">>> Services already exist.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    populate_services()
