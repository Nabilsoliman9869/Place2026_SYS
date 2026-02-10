# [file name]: diagnose.py
#!/usr/bin/env python3
"""
تشخيص النظام الحالي - تشغيل هذا الملف أولاً
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"🔍 {text}")
    print("="*60)

def check_file_exists(filename, required=True):
    exists = os.path.exists(filename)
    status = "✅ موجود" if exists else "❌ مفقود"
    if required and not exists:
        status += " (مطلوب)"
    print(f"   {filename}: {status}")
    return exists

def check_python_deps():
    print_header("فحص المكتبات المطلوبة")
    
    required_packages = [
        'flask',
        'flask_cors',
        'pyodbc',
        'qrcode',
        'PIL'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   {package}: ✅ مثبت")
        except ImportError:
            print(f"   {package}: ❌ غير مثبت")

def analyze_app_py():
    print_header("تحليل app.py")
    
    if not os.path.exists('app.py'):
        print("❌ ملف app.py غير موجود")
        return
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    stats = {
        'lines': len(content.split('\n')),
        'has_database': 'import database' in content,
        'has_routes': content.count('@app.route'),
        'has_api': content.count('/api/') > 0,
        'has_templates': 'render_template' in content
    }
    
    print(f"   عدد الأسطر: {stats['lines']}")
    print(f"   يتضمن قاعدة بيانات: {'✅ نعم' if stats['has_database'] else '❌ لا'}")
    print(f"   عدد المسارات: {stats['has_routes']}")
    print(f"   واجهات API: {stats['has_api']}")
    print(f"   يستخدم القوالب: {'✅ نعم' if stats['has_templates'] else '❌ لا'}")
    
    # البحث عن المشاكل
    if 'HTML في السلسلة' in content:
        print("   ⚠️  يحتوي على HTML مضمن (يجب فصله)")
    
    return stats

def analyze_database_py():
    print_header("تحليل database.py")
    
    if not os.path.exists('database.py'):
        print("❌ ملف database.py غير موجود")
        return
    
    with open('database.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # عد الدوال
    functions = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and ':' in line:
            func_name = line.split('def ')[1].split('(')[0].strip()
            functions.append(func_name)
    
    print(f"   عدد الدوال: {len(functions)}")
    print(f"   الدوال الرئيسية: {', '.join(functions[:10])}")
    
    # التحقق من الجداول
    tables = []
    if 'CREATE TABLE' in content:
        # استخراج أسماء الجداول
        import re
        table_matches = re.findall(r'CREATE TABLE (\w+)', content)
        tables.extend(table_matches)
    
    print(f"   الجداول المذكورة: {len(tables)} جدول")
    if tables:
        print(f"   أسماء الجداول: {', '.join(tables[:10])}")

def test_system_startup():
    print_header("اختبار تشغيل النظام")
    
    if not os.path.exists('app.py'):
        print("❌ لا يمكن التشغيل بدون app.py")
        return False
    
    try:
        # محاولة تشغيل النظام لفترة قصيرة
        print("   جاري تشغيل النظام...")
        
        # استيراد app لفهم هيكله
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # محاولة قراءة بعض المعلومات
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # البحث عن معلومات التشغيل
        if 'app.run(' in app_content:
            run_line = [l for l in app_content.split('\n') if 'app.run(' in l][0]
            print(f"   إعدادات التشغيل: {run_line.strip()}")
        
        print("   ✅ تم تحليل ملف app.py بنجاح")
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في التحليل: {e}")
        return False

def check_directory_structure():
    print_header("فحص هيكل المجلدات")
    
    current_files = os.listdir('.')
    print(f"   الملفات الموجودة: {len(current_files)} ملف")
    
    # تصنيف الملفات
    categories = {
        'Python Files': [f for f in current_files if f.endswith('.py')],
        'HTML Files': [f for f in current_files if f.endswith('.html')],
        'Config Files': [f for f in current_files if f.endswith('.ini') or f.endswith('.cfg') or f == 'config.py'],
        'Other Files': [f for f in current_files if not f.endswith(('.py', '.html', '.ini', '.cfg')) and '.' in f]
    }
    
    for category, files in categories.items():
        if files:
            print(f"   {category}: {len(files)} ملف")
            for f in files[:5]:  # عرض أول 5 ملفات فقط
                print(f"     - {f}")
            if len(files) > 5:
                print(f"     ... و{len(files)-5} ملفات أخرى")

def main():
    print("🚀 بدء تشخيص نظام الموارد البشرية")
    print("="*60)
    
    # 1. فحص الملفات الأساسية
    print_header("الملفات الأساسية")
    essential_files = [
        'app.py',
        'database.py', 
        'config.py',
        'index.html'
    ]
    
    file_status = {}
    for file in essential_files:
        file_status[file] = check_file_exists(file, required=True)
    
    # 2. فحص المكتبات
    check_python_deps()
    
    # 3. تحليل الملفات
    app_stats = analyze_app_py()
    analyze_database_py()
    
    # 4. فحص الهيكل
    check_directory_structure()
    
    # 5. اختبار التشغيل
    can_run = test_system_startup()
    
    # 6. التلخيص
    print_header("نتائج التشخيص")
    
    missing_essential = [f for f, exists in file_status.items() if not exists]
    
    if missing_essential:
        print("❌ المشاكل الحرجة:")
        for file in missing_essential:
            print(f"   - {file} مفقود")
    else:
        print("✅ جميع الملفات الأساسية موجودة")
    
    if can_run:
        print("✅ النظام يمكن تشغيله")
    else:
        print("⚠️  قد تكون هناك مشاكل في التشغيل")
    
    print("\n📋 الخطوات التالية المقترحة:")
    print("   1. تشغيل: python app.py")
    print("   2. زيارة: http://localhost:5000")
    print("   3. اختبار: http://localhost:5000/test")
    
    return len(missing_essential) == 0

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)