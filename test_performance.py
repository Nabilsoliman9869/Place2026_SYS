import time
import pyodbc
import json
import sys

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
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;Connect Timeout=30;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};Connect Timeout=30;'

def benchmark():
    print("\n📊 Starting System Performance Test...")
    print("========================================")
    
    conn_str = get_db_connection_string()
    try:
        server_name = conn_str.split('SERVER=')[1].split(';')[0]
        print(f"🔌 Connecting to Database: {server_name}")
    except:
        print(f"🔌 Connecting to Database...")

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("✅ Connection Successful!")
        
        # Test 1: Network Latency
        print("\n1️⃣  Testing Network Latency (Ping)...")
        start = time.time()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        latency = (time.time() - start) * 1000
        print(f"   ⏱️  Response Time: {latency:.2f} ms")
        if latency > 100:
            print("   ⚠️  High Latency Detected (Remote Server). Optimizations are CRITICAL.")
        else:
            print("   ✅ Latency is Good.")

        # Test 2: Dropdown Performance (Candidates)
        print("\n2️⃣  Testing Dropdown Data Load (Top 200)...")
        start = time.time()
        cursor.execute("SELECT TOP 200 CandidateID, FullName, Phone FROM Candidates ORDER BY CreatedAt DESC")
        rows = cursor.fetchall()
        duration = (time.time() - start) * 1000
        print(f"   ⏱️  Load Time: {duration:.2f} ms")
        print(f"   📦 Rows Fetched: {len(rows)}")
        if duration < 500:
            print("   ✅ Dropdown Load Speed is Excellent.")
        else:
            print("   ⚠️  Dropdown Load is Slow.")

        # Test 3: Search Performance (Indexed)
        print("\n3️⃣  Testing Search Performance (Phone Index)...")
        start = time.time()
        cursor.execute("SELECT COUNT(*) FROM Candidates WHERE Phone LIKE '010%'")
        count = cursor.fetchone()[0]
        duration = (time.time() - start) * 1000
        print(f"   ⏱️  Search Time: {duration:.2f} ms")
        print(f"   magnifying_glass_tilted_right Candidates Found: {count}")
        
        print("\n========================================")
        print("🎉 DIAGNOSIS COMPLETE")
        print("If all checks passed with low times, the system is optimized.")
        print("========================================")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Connection or Test Failed: {e}")
        print("Please check your internet connection or VPN if using a remote database.")

if __name__ == "__main__":
    benchmark()
