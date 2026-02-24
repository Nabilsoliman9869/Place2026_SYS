import os
import shutil
from pathlib import Path

print("🛠️ إنشاء هيكل المجلدات...")

# 1. إنشاء مجلد templates
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)
print("✅ تم إنشاء مجلد templates")

# 2. إذا كان index.html موجوداً في المجلد الرئيسي، انقله
if os.path.exists("index.html"):
    try:
        shutil.move("index.html", "templates/index.html")
        print("✅ تم نقل index.html إلى templates/")
    except Exception as e:
        print(f"⚠️ لم استطع نقل index.html: {e}")
        # أنشئ نسخة جديدة
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head><title>النظام</title></head>
<body><h1>النظام يعمل</h1></body>
</html>""")
        print("✅ تم إنشاء templates/index.html جديد")
else:
    print("ℹ️ index.html غير موجود في المجلد الرئيسي")
    # أنشئ index.html بسيط في templates
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head><title>نظام الموارد البشرية</title></head>
<body>
<h1>🚀 نظام إدارة الموارد البشرية</h1>
<p>الصفحة الرئيسية - جاري التطوير</p>
<a href="/test">اختبار النظام</a>
</body>
</html>""")
    print("✅ تم إنشاء templates/index.html")

# 3. إنشاء باقي المجلدات المطلوبة
folders = ['static/css', 'static/js', 'static/images', 'logs']
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(f"✅ تم إنشاء {folder}")

print("\n🎉 تم الانتهاء!")
print("\n📋 الملفات الحالية:")
for item in os.listdir('.'):
    if os.path.isdir(item):
        print(f"📁 {item}/")
    else:
        print(f"📄 {item}")