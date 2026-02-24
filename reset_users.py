from app import app, get_db

def reset_passwords():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        print(">>> Resetting all passwords to '123'...")
        cursor.execute("UPDATE Users_1 SET Password='123'")
        db.commit()
        print(">>> SUCCESS: All passwords are now '123'")
        
        print("\n>>> Generating Updated User List:")
        cursor.execute("SELECT FullName, Username, Role FROM Users_1 ORDER BY Role, Username")
        users = cursor.fetchall()
        
        print(f"{'FullName':<30} | {'Username':<25} | {'Role':<15} | {'Password'}")
        print("-" * 85)
        for u in users:
            fname = u[0] if u[0] else "N/A"
            uname = u[1] if u[1] else "N/A"
            role = u[2] if u[2] else "N/A"
            print(f"{fname:<30} | {uname:<25} | {role:<15} | 123")

if __name__ == "__main__":
    reset_passwords()
