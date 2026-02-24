import database as db
import sys

try:
    print("Testing database connection...")
    if db.test_connection():
        print("✅ Connection successful!")
        
        # Try a simple query
        print("Testing query...")
        stats = db.get_dashboard_stats()
        print(f"Stats retrieved: {stats}")
        
    else:
        print("❌ Connection failed!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
