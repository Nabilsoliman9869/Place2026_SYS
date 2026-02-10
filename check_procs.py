from app import app, query_db

def check_procedures():
    with app.app_context():
        try:
            # Query system catalog for user-defined stored procedures
            procs = query_db("SELECT name FROM sys.objects WHERE type = 'P' AND is_ms_shipped = 0")
            proc_names = [p['name'] for p in procs] if procs else []
            
            print(f"User Stored Procedures found: {len(proc_names)}")
            if proc_names:
                print(f"Names: {proc_names}")
            else:
                print("No custom stored procedures found. Logic is handled in Python.")
                
        except Exception as e:
            print(f"Error checking procedures: {e}")

if __name__ == "__main__":
    check_procedures()
