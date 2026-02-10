import pandas as pd
import pyodbc
import json
import os
from datetime import datetime

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

def clean_text(text):
    if pd.isna(text): return None
    return str(text).strip()

def import_placements_plan():
    print("🚀 Starting Phase 3 Import: Hiring Plans...")
    file_path = 'Guide Academy Placements 2025.xlsx'
    
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    try:
        conn = pyodbc.connect(get_db_connection_string())
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    # Target Sheets for Plans
    plan_sheets = ['Jan Hiring Plan', 'Feb Hiring Plan', 'April Hiring Plan']
    
    for sheet in plan_sheets:
        try:
            print(f"\n📄 Processing Sheet: {sheet}...")
            # Note: We need to inspect structure first, but let's assume standard format or just read row by row
            # Usually hiring plans have: Company, Role, Count, Deadline
            # Let's peek at the first few rows to infer structure
            df = pd.read_excel(file_path, sheet_name=sheet)
            
            # If sheet is empty
            if df.empty:
                print("   ⚠️ Sheet is empty.")
                continue

            # We'll treat the sheet name itself as a "Campaign" or "Request Group"
            # But let's look for client names in the sheet to create requests
            
            # Heuristic: Find columns like 'Account', 'Client', 'LOB', 'HC' (Headcount)
            # Let's iterate rows and try to extract "Account" and "Headcount"
            
            # Common structure: 
            # Account | LOB | Headcount | Wave Date
            
            # Map columns
            account_col = None
            hc_col = None
            lob_col = None
            
            for col in df.columns:
                h = str(col).lower()
                if 'account' in h or 'client' in h: account_col = col
                if 'hc' in h or 'count' in h or 'target' in h: hc_col = col
                if 'lob' in h or 'role' in h or 'title' in h: lob_col = col

            if not account_col:
                # Fallback: Col 0 is usually Account
                if len(df.columns) > 0: account_col = df.columns[0]
            
            if not hc_col:
                # Fallback: Look for numeric column
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        hc_col = col
                        break
            
            print(f"   🔍 Mapping: Account='{account_col}', HC='{hc_col}'")
            
            count_req = 0
            for index, row in df.iterrows():
                client_name = clean_text(row.get(account_col))
                if not client_name or client_name.lower() == 'nan': continue
                if 'total' in client_name.lower(): continue

                # Get/Create Client
                cursor.execute("SELECT ClientID FROM Clients WHERE CompanyName = ?", (client_name,))
                c_row = cursor.fetchone()
                if c_row:
                    client_id = c_row[0]
                else:
                    cursor.execute("INSERT INTO Clients (CompanyName, CreatedAt) VALUES (?, GETDATE())", (client_name,))
                    conn.commit()
                    cursor.execute("SELECT @@IDENTITY")
                    client_id = cursor.fetchone()[0]
                    print(f"   ➕ Created Client: {client_name}")

                # Get Details
                needed = 0
                if hc_col:
                    try:
                        val = row.get(hc_col)
                        if pd.notna(val): needed = int(val)
                    except: pass
                
                job_title = clean_text(row.get(lob_col)) if lob_col else f"Agent ({sheet})"
                if not job_title or job_title == 'None': job_title = f"Agent - {sheet}"

                # Create Request
                cursor.execute("""
                    INSERT INTO ClientRequests (ClientID, JobTitle, NeededCount, Status, CreatedAt, Requirements)
                    VALUES (?, ?, ?, 'Open', GETDATE(), ?)
                """, (client_id, job_title, needed, f"Imported from {sheet}"))
                conn.commit()
                count_req += 1
            
            print(f"   ✅ Created {count_req} requests from {sheet}.")

        except Exception as e:
            print(f"   ⚠️ Error processing {sheet}: {e}")

    conn.close()

if __name__ == "__main__":
    import_placements_plan()
