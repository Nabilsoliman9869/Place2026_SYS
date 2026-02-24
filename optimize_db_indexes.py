import pyodbc
import json

CONFIG_FILE = 'db_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def get_db_connection_string():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;Connect Timeout=60;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};Connect Timeout=60;'

def optimize_indexes():
    conn_str = get_db_connection_string()
    print(f"Connecting to: {conn_str.split(';')[1]}...")
    
    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Extended List of Indexes
        indexes = [
            # Candidates
            ("Candidates", "IX_Candidates_Phone", "Phone"),
            ("Candidates", "IX_Candidates_SalesAgentID", "SalesAgentID"),
            ("Candidates", "IX_Candidates_CreatedAt", "CreatedAt"),
            ("Candidates", "IX_Candidates_Status", "Status"),
            ("Candidates", "IX_Candidates_FullName", "FullName"), # For search
            
            # TA Schedules
            ("TASchedules", "IX_TASchedules_SlotDate", "SlotDate"),
            ("TASchedules", "IX_TASchedules_Status", "Status"),
            ("TASchedules", "IX_TASchedules_EvaluatorID", "EvaluatorID"),
            
            # Invoices & Finance
            ("InvoiceHeaders", "IX_InvoiceHeaders_CandidateID", "CandidateID"),
            ("InvoiceHeaders", "IX_InvoiceHeaders_Status", "Status"),
            ("InvoiceHeaders", "IX_InvoiceHeaders_InvoiceDate", "InvoiceDate"),
            ("GeneralSales", "IX_GeneralSales_SaleDate", "SaleDate"),
            
            # Training
            ("Enrollments", "IX_Enrollments_BatchID", "BatchID"),
            ("Enrollments", "IX_Enrollments_CandidateID", "CandidateID"),
            ("CourseBatches", "IX_CourseBatches_Status", "Status"),
            
            # Requests
            ("ClientRequests", "IX_ClientRequests_Status", "Status"),
            ("ClientRequests", "IX_ClientRequests_ClientID", "ClientID"),
        ]
        
        print("\n--- Starting Extended Index Optimization ---")
        
        for table, idx_name, column in indexes:
            try:
                # Check if table exists first
                check_table = f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table}'"
                cursor.execute(check_table)
                if cursor.fetchone()[0] == 0:
                    print(f"Skipping {idx_name}: Table {table} not found.")
                    continue

                # Check if index exists
                check_idx = f"SELECT count(*) FROM sys.indexes WHERE name = '{idx_name}' AND object_id = OBJECT_ID('{table}')"
                cursor.execute(check_idx)
                if cursor.fetchone()[0] == 0:
                    print(f"Creating index {idx_name} on {table}({column})...")
                    cursor.execute(f"CREATE INDEX {idx_name} ON {table} ({column})")
                    print("  -> Done.")
                else:
                    print(f"Index {idx_name} already exists.")
            except Exception as e:
                print(f"  -> Failed to create {idx_name}: {e}")

        print("\n--- Optimization Complete ---")
        conn.close()
        
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    optimize_indexes()
