import database as db

def add_corp_user():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM SystemUsers WHERE Username = 'corporate'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO SystemUsers (Username, Password, Role, Department, FullName)
                VALUES ('corporate', 'corp123', 'Employee', 'Corporate', 'مسؤول خدمة الشركات')
            """)
            conn.commit()
            print("✅ تم إضافة مستخدم corporate")
        else:
            print("ℹ️ مستخدم corporate موجود بالفعل")
    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_corp_user()
