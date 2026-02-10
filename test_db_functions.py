import database as db
import datetime

def test_functions():
    print("Testing database functions...")
    try:
        print("1. get_dashboard_stats...", end="")
        db.get_dashboard_stats()
        print("OK")
        
        print("2. fetch_all...", end="")
        db.fetch_all("SELECT 1")
        print("OK")
        
        print("3. get_all_interests...", end="")
        db.get_all_interests()
        print("OK")
        
        print("4. get_placement_exams...", end="")
        db.get_placement_exams()
        print("OK")
        
        print("5. get_all_candidates...", end="")
        db.get_all_candidates()
        print("OK")
        
        print("6. get_all_trainings...", end="")
        db.get_all_trainings()
        print("OK")
        
        print("7. get_all_clients...", end="")
        db.get_all_clients()
        print("OK")
        
        print("8. get_pending_invoices...", end="")
        db.get_pending_invoices()
        print("OK")
        
        print("All database functions verified successfully!")
        
    except Exception as e:
        print(f"\nFAIL: {e}")

if __name__ == "__main__":
    test_functions()
