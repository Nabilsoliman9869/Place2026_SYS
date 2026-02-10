# init_database.py - نسخة عملية
"""
ملف تهيئة قاعدة البيانات للنظام
"""

import database as db

def initialize_with_retry():
    """تهيئة مع إعادة المحاولة"""
    print("🔧 بدء تهيئة النظام...")
    print("=" * 60)
    
    # اختبار الاتصال أولاً
    print("1. اختبار اتصال قاعدة البيانات...")
    try:
        if db.test_connection():
            print("✅ اتصال قاعدة البيانات ناجح")
        else:
            print("❌ فشل الاتصال بقاعدة البيانات")
            return False
    except Exception as e:
        print(f"⚠️  خطأ في اختبار الاتصال: {e}")
        # نستمر رغم الخطأ
    
    # محاولة تهيئة الجداول
    print("\n2. تهيئة الجداول الأساسية...")
    try:
        success = db.init_database()
        if success:
            print("✅ تمت تهيئة الجداول بنجاح")
        else:
            print("⚠️  قد تكون الجداول موجودة بالفعل - نستمر...")
    except Exception as e:
        print(f"⚠️  خطأ في تهيئة الجداول: {e}")
        # نستمر رغم الخطأ
    
    # إضافة بيانات تجريبية
    print("\n3. إضافة بيانات تجريبية...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # فحص إذا كانت البيانات موجودة بالفعل
        cursor.execute("SELECT COUNT(*) FROM Candidates")
        existing_candidates = cursor.fetchone()[0]
        
        if existing_candidates > 0:
            print(f"⚠️  يوجد بالفعل {existing_candidates} مرشح في النظام")
            response = input("هل تريد إضافة بيانات إضافية؟ (نعم/لا): ").strip().lower()
            if response not in ['نعم', 'yes', 'y']:
                conn.close()
                print("✅ تم الحفاظ على البيانات الحالية")
                return True
        
        # البيانات الأساسية
        print("إضافة البيانات الأساسية...")
        
        # إضافة مرشحين (بتجنب التكرار)
        candidates = [
            ('أحمد محمد علي', '0512345678', 'ahmed@example.com', 32, 'ذكر', '1234567890'),
            ('سارة خالد الحربي', '0554321789', 'sara@example.com', 28, 'أنثى', '0987654321'),
            ('محمد عبدالله الشمري', '0509876543', 'mohammed@example.com', 35, 'ذكر', '1122334455'),
        ]
        
        added = 0
        for fullname, phone, email, age, gender, national_id in candidates:
            # التحقق إذا كان المرشح موجوداً
            cursor.execute("SELECT COUNT(*) FROM Candidates WHERE Phone = ? OR NationalID = ?", (phone, national_id))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO Candidates (FullName, Phone, Email, Age, Gender, NationalID, 
                    Address, EducationLevel, LanguageLevel, ComputerSkills, WorkExperience, ExpectedSalary, Status)
                    VALUES (?, ?, ?, ?, ?, ?, 'عنوان افتراضي', 'بكالوريوس', 'متوسط', 'مهارات أساسية', 'خبرة متنوعة', 10000, 'جديد')
                """, (fullname, phone, email, age, gender, national_id))
                added += 1
        
        print(f"✅ تم إضافة {added} مرشح جديد")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة البيانات: {e}")
        return False

def show_current_status():
    """عرض الحالة الحالية"""
    print("\n📊 حالة النظام الحالية:")
    print("-" * 40)
    
    try:
        # جلب الإحصائيات
        stats = db.get_dashboard_stats()
        
        print(f"👥 المرشحين: {stats.get('total_candidates', 0)}")
        print(f"📞 تسجيلات الاهتمام: {stats.get('total_interests', 0)}")
        print(f"📈 تسجيلات اليوم: {stats.get('today_leads', 0)}")
        print(f"🎓 دورات تدريبية نشطة: {stats.get('active_trainings', 0)}")
        print(f"🏢 عملاء نشطين: {stats.get('active_clients', 0)}")
        
    except Exception as e:
        print(f"⚠️  لا يمكن عرض الإحصائيات: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 نظام إدارة الموارد البشرية")
    print("=" * 60)
    
    print("""
خيارات التهيئة:
1. تهيئة كاملة (جداول + بيانات)
2. عرض الحالة الحالية فقط
3. إضافة بيانات تجريبية فقط
4. الخروج
""")
    
    choice = input("اختر رقم الخيار (1-4): ").strip()
    
    if choice == "1":
        # تهيئة كاملة
        success = initialize_with_retry()
        if success:
            show_current_status()
            print("\n🎉 تم اكتمال التهيئة بنجاح!")
        else:
            print("\n⚠️  حدثت بعض المشاكل خلال التهيئة")
    
    elif choice == "2":
        # عرض الحالة فقط
        show_current_status()
    
    elif choice == "3":
        # إضافة بيانات فقط
        print("\nإضافة بيانات تجريبية...")
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # إضافة مرشح واحد للتجربة
            cursor.execute("""
                INSERT INTO Candidates (FullName, Phone, Email, Age, Gender, NationalID, 
                Address, EducationLevel, LanguageLevel, ComputerSkills, WorkExperience, ExpectedSalary, Status)
                VALUES ('مرشح تجريبي', '0511111111', 'test@example.com', 30, 'ذكر', '9999999999',
                'عنوان تجريبي', 'بكالوريوس', 'متوسط', 'مهارات حاسوب', 'خبرة 5 سنوات', 12000, 'جديد')
            """)
            
            conn.commit()
            conn.close()
            print("✅ تم إضافة مرشح تجريبي بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في إضافة البيانات: {e}")
    
    elif choice == "4":
        print("✅ تم الخروج")
        return
    
    else:
        print("❌ خيار غير صحيح")
    
    # عرض التعليمات النهائية
    print("\n" + "=" * 60)
    print("🔗 روابط النظام:")
    print("   http://localhost:5000 - الصفحة الرئيسية")
    print("   http://localhost:5000/test - صفحة الاختبار")
    print("\n🔐 بيانات الدخول:")
    print("   👤 المستخدم: admin")
    print("   🔑 كلمة المرور: admin@123")
    print("\n🚀 لتشغيل النظام:")
    print("   python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()