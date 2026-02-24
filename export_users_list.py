from app import app, get_db

def export_all_users():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT FullName, Username, Role FROM Users_1 ORDER BY Role, Username")
        users = cursor.fetchall()
        
        output_file = "All_Users_Credentials.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{'FullName':<40} | {'Username':<25} | {'Role':<20} | {'Password'}\n")
            f.write("-" * 100 + "\n")
            for u in users:
                fname = u[0] if u[0] else "N/A"
                uname = u[1] if u[1] else "N/A"
                role = u[2] if u[2] else "N/A"
                line = f"{fname:<40} | {uname:<25} | {role:<20} | 123\n"
                f.write(line)
        
        print(f"Successfully exported {len(users)} users to {output_file}")

if __name__ == "__main__":
    export_all_users()
