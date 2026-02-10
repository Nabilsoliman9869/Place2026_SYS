import database as db
import hashlib

def test_login():
    username = "manager"
    password = "manager123"
    
    print(f"Testing login for {username}...")
    
    # 1. Check if user exists in DB
    conn = db.get_db_connection()
    user_record = conn.execute("SELECT * FROM Users WHERE Username = ?", (username,)).fetchone()
    conn.close()
    
    if not user_record:
        print("❌ User 'manager' not found in database!")
        return
    
    print("✅ User 'manager' found in database.")
    print(f"   Stored Hash: {user_record['PasswordHash']}")
    
    # 2. Check password hashing
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"   Input Hash:  {input_hash}")
    
    if input_hash == user_record['PasswordHash']:
        print("✅ Password hash matches.")
    else:
        print("❌ Password hash DOES NOT match.")
        return

    # 3. Test authenticate_user function
    user = db.authenticate_user(username, password)
    if user:
        print("✅ db.authenticate_user() returned success.")
        print(f"   Role: {user['Role']}, Department: {user['Department']}")
    else:
        print("❌ db.authenticate_user() returned None.")

if __name__ == "__main__":
    test_login()
