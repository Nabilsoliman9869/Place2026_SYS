# test_system_complete.py
"""
ملف اختبار شامل لنظام إدارة الموارد البشرية
يفحص جميع المكونات والملفات
"""

import os
import sys
import importlib
import subprocess
from datetime import datetime

print("🔍 بدء الفحص الشامل للنظام...")
print("=" * 60)

def check_file_exists(file_path, required=True):
    """فحص وجود ملف"""
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
        return True
    else:
        if required:
            print(f"❌ {file_path} (مفقود)")
        else:
            print(f"⚠️  {file_path} (اختياري - مفقود)")
        return False

def check_folder_exists(folder_path, required=True):
    """فحص وجود مجلد"""
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"📁 {folder_path}/")
        return True
    else:
        if required:
            print(f"❌ {folder_path}/ (مفقود)")
        else:
            print(f"⚠️  {folder_path}/ (اختياري - مفقود)")
        return False

def check_python_module(module_name):
    """فحص إمكانية استيراد موديول بايثون"""
    try:
        importlib.import_module(module_name)
        print(f"✅ موديول: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ موديول: {module_name} - {e}")
        return False

def check_file_content(file_path, min_size=100):
    """فحص محتوى الملف"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size >= min_size:
            print(f"   📊 حجم: {size} بايت")
            return True
        else:
            print(f"   ⚠️  حجم صغير: {size} بايت (أقل من {min_size} بايت)")
            return False
    return False

print("\n📁 فحص هيكل المجلدات والملفات:")
print("-" * 40)

# فحص المجلدات الأساسية
folders = [
    'templates',
    'static',
    'static/css',
    'static/js', 
    'static/images',
    'logs'
]

for folder in folders:
    check_folder_exists(folder, required=('logs' not in folder))

print("\n📄 فحص الملفات الأساسية:")
print("-" * 40)

# فحص الملفات الأساسية
files = [
    ('app.py', True, 1000),
    ('database.py', True, 500),
    ('config.py', True, 100),
    ('requirements.txt', True, 50),
    ('.env', False, 10),
    ('templates/index.html', True, 500),
    ('static/css/style.css', False, 100),
    ('static/js/main.js', False, 100),
]

missing_files = []
for file_path, required, min_size in files:
    if check_file_exists(file_path, required):
        check_file_content(file_path, min_size)
    elif required:
        missing_files.append(file_path)

print("\n🐍 فحص متطلبات Python:")
print("-" * 40)

# فحص الموديولات الأساسية
modules = [
    'flask',
    'flask_cors',
    'jwt',
    'argon2',
    'pyodbc',
    'dotenv'
]

missing_modules = []
for module in modules:
    if not check_python_module(module):
        missing_modules.append(module)

print("\n🔧 فحص تكوين التطبيق:")
print("-" * 40)

try:
    # محاولة استيراد app.py
    sys.path.insert(0, '.')
    from app import app
    
    print("✅ تم استيراد app.py بنجاح")
    
    # فحص عدد المسارات في التطبيق
    routes = []
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.endpoint:
            routes.append(str(rule))
    
    print(f"   🛣️  عدد المسارات: {len(routes)}")
    
    # عرض أهم المسارات
    print("   📍 المسارات الرئيسية:")
    important_routes = ['/', '/dashboard', '/login', '/api/health', '/api/candidates']
    for route in routes:
        for important in important_routes:
            if important in route:
                print(f"      • {route}")
                break
    
except Exception as e:
    print(f"❌ خطأ في استيراد app.py: {e}")

print("\n🔌 فحص اتصال قاعدة البيانات:")
print("-" * 40)

try:
    import database as db
    print("✅ تم استيراد database.py")
    
    # محاولة الاتصال
    try:
        conn = db.get_connection()
        print("✅ الاتصال بقاعدة البيانات ناجح")
        
        # محاولة جلب البيانات
        try:
            candidates = db.get_all_candidates()
            print(f"✅ جلب البيانات: {len(candidates) if candidates else 0} مرشح")
            conn.close()
        except Exception as e:
            print(f"⚠️  خطأ في جلب البيانات: {e}")
            
    except Exception as e:
        print(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
        
except Exception as e:
    print(f"❌ خطأ في استيراد database.py: {e}")

print("\n🌐 فحص خدمة الويب:")
print("-" * 40)

# محاولة تشغيل الخادم في الخلفية واختباره
try:
    # اختبار بسيط للخدمة
    import http.client
    import json
    
    # إنشاء اتصال محلي
    conn = http.client.HTTPConnection("localhost", 5000, timeout=5)
    
    try:
        # محاولة الوصول إلى صفحة الصحة
        conn.request("GET", "/api/health")
        response = conn.getresponse()
        
        if response.status == 200:
            data = json.loads(response.read().decode())
            print(f"✅ الخدمة تعمل (الحالة: {data.get('status', 'unknown')})")
        else:
            print(f"⚠️  الخدمة تستجيب ولكن بحالة: {response.status}")
            
    except ConnectionRefusedError:
        print("❌ الخدمة غير نشطة (لم يتم بدء تشغيل الخادم)")
    except Exception as e:
        print(f"⚠️  خطأ في الاتصال: {e}")
        
    finally:
        conn.close()
        
except Exception as e:
    print(f"⚠️  فحص الخدمة: {e}")

print("\n📋 ملخص النتائج:")
print("-" * 40)
print(f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# حساب النتائج
issues = []

if missing_files:
    issues.append(f"الملفات المفقودة: {len(missing_files)}")
    
if missing_modules:
    issues.append(f"الموديولات المفقودة: {len(missing_modules)}")

if not os.path.exists('templates/index.html'):
    issues.append("index.html مفقود في templates/")

if issues:
    print("⚠️  المشاكل التي تحتاج للحل:")
    for issue in issues:
        print(f"   • {issue}")
else:
    print("✅ النظام جاهز للتشغيل!")

print("\n🚀 خطوات التشغيل:")
print("-" * 40)
print("1. تثبيت المتطلبات:")
print("   pip install -r requirements.txt")
print("\n2. تشغيل التطبيق:")
print("   python app.py")
print("\n3. الوصول للتطبيق:")
print("   http://localhost:5000")
print("\n4. تسجيل الدخول:")
print("   المستخدم: admin")
print("   كلمة المرور: admin@123")

print("\n" + "=" * 60)
print("🎯 الفحص اكتمل!")
print("=" * 60)

# اقتراحات للتحسين
print("\n💡 اقتراحات للتحسين:")
if missing_modules:
    print("   • تثبيت الموديولات المفقودة:")
    for module in missing_modules:
        print(f"     pip install {module}")

if not os.path.exists('.env'):
    print("   • إنشاء ملف .env من .env.txt:")
    print("     cp .env.txt .env")

if not os.path.exists('templates/index.html'):
    print("   • إنشاء templates/index.html باستخدام:")
    print("     python create_structure.py")