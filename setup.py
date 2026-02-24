"""
إعداد المشروع - تشغيل مرة واحدة لإنشاء الهيكل
"""
import os
import shutil
from pathlib import Path

def setup_project():
    print("🚀 بدء إعداد مشروع نظام الموارد البشرية")
    print("=" * 60)
    
    # إنشاء المجلدات الأساسية
    folders = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'templates/partials',
        'logs',
        'backups',
        'uploads'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 تم إنشاء: {folder}")
    
    # نسخ الملفات الحالية إذا كانت موجودة
    files_to_copy = {
        'app.py': 'app_old.py',
        'database.py': 'database_old.py',
        'index.html': 'templates/old_index.html'
    }
    
    for src, dst in files_to_copy.items():
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"📄 تم نسخ: {src} → {dst}")
    
    # إنشاء ملفات أساسية جديدة
    print("\n📝 إنشاء الملفات الأساسية...")
    
    # 1. ملف المتطلبات
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write("""Flask==2.3.3
Flask-CORS==4.0.0
pyodbc==5.0.1
qrcode==7.4.2
Pillow==10.0.0
python-dotenv==1.0.0
pyjwt==2.8.0
argon2-cffi==23.1.0
python-dateutil==2.8.2
""")
    
    # 2. ملف البيئة
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write("""# إعدادات قاعدة البيانات
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=Place2026
DB_USER=sa
DB_PASSWORD=YourPassword123

# إعدادات التطبيق
SECRET_KEY=change-this-in-production-very-secret-key
JWT_SECRET=another-secret-key-for-jwt-tokens
DEBUG=True
LOG_LEVEL=INFO

# إعدادات البريد
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password

# إعدادات أخرى
SESSION_TIMEOUT=24
PAGE_SIZE=20
BACKUP_DAYS=7
""")
    
    # 3. ملف Docker لوضعية التشغيل (اختياري)
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write("""FROM python:3.9-slim

WORKDIR /app

# تثبيت ODBC للسيرفر
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ التطبيق
COPY . .

# فتح المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["python", "app.py"]
""")
    
    # 4. ملف تهيئة قاعدة البيانات
    with open('init_db.py', 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
"""
تهيئة قاعدة البيانات - يجب تشغيله مرة واحدة
"""
import sys
import os
sys.path.append('.')
from database import init_database

if __name__ == '__main__':
    print("🔧 بدء تهيئة قاعدة البيانات...")
    try:
        success = init_database()
        if success:
            print("✅ تمت التهيئة بنجاح!")
            print("\n📊 يمكنك الآن:")
            print("   1. تشغيل التطبيق: python app.py")
            print("   2. زيارة http://localhost:5000")
            print("   3. تسجيل الدخول باستخدام admin/admin@123")
        else:
            print("❌ فشلت التهيئة. تحقق من اتصال قاعدة البيانات.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        sys.exit(1)
""")
    
    print("\n" + "=" * 60)
    print("✅ تم إعداد المشروع بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("   1. قم بنسخ .env.example إلى .env وعدل الإعدادات")
    print("   2. قم بتشغيل: python init_db.py")
    print("   3. قم بتشغيل: python app.py")
    print("=" * 60)

if __name__ == '__main__':
    setup_project()