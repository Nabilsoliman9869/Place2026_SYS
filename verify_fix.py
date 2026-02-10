
import os
from app import app, query_db

def verify_dashboard():
    print("🔍 Starting Verification...")
    
    # Create a context to access DB
    with app.app_context():
        # 1. Find a Manager user to test with
        try:
            user = query_db("SELECT TOP 1 UserID, Username FROM Users_1 WHERE Role = ?", ('Manager',), one=True)
            if not user:
                print("❌ No Manager user found in DB. Cannot fully test RBAC.")
                # Fallback to creating a temp manager? No, let's try 'Admin'
                user = query_db("SELECT TOP 1 UserID, Username FROM Users_1 WHERE Role = ?", ('Admin',), one=True)
                if not user:
                    print("❌ No Admin user found either.")
                    return
            
            print(f"✅ Found Test User: {user['Username']} (ID: {user['UserID']})")
            
            # 2. Test Dashboard Access
            with app.test_client() as client:
                # Simulate Login Session
                with client.session_transaction() as sess:
                    sess['user_id'] = user['UserID']
                    sess['role'] = 'Manager'
                
                print("🔄 Requesting /dashboard...")
                response = client.get('/dashboard')
                
                if response.status_code == 200:
                    content = response.data.decode('utf-8')
                    # Check for key elements from the new sidebar
                    if "check_role_access" in content: 
                         # This would mean the template failed to render the function call and printed it? 
                         # No, usually it throws error.
                         pass
                    
                    if "Central Command" in content:
                        print("✅ SUCCESS: Dashboard rendered correctly!")
                        print("   - 'Central Command' found.")
                        print("   - Sidebar loaded without Jinja errors.")
                    else:
                        print("⚠️ WARNING: Dashboard rendered (200 OK) but 'Central Command' text missing.")
                        print("   This might mean the old template is still caching or logic differs.")
                else:
                    print(f"❌ FAILED: Status Code {response.status_code}")
                    print("   Error Output:")
                    print(response.data.decode('utf-8')[:500]) # Print first 500 chars of error

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    verify_dashboard()
