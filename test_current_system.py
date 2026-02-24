# test_current_system.py
import subprocess
import requests
import time

def test_current_system():
    print("🔍 اختبار النظام الحالي...")
    
    # 1. اختبار تشغيل app.py
    print("\n1. اختبار تشغيل app.py...")
    try:
        process = subprocess.Popen(['python', 'app.py'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        time.sleep(3)
        
        # 2. اختبار API
        print("\n2. اختبار واجهات API...")
        urls_to_test = [
            'http://localhost:5000/',
            'http://localhost:5000/login',
            'http://localhost:5000/test',
            'http://localhost:5000/api/test/connection'
        ]
        
        for url in urls_to_test:
            try:
                response = requests.get(url, timeout=5)
                print(f"   {url}: {'✅' if response.status_code == 200 else '❌'} {response.status_code}")
            except:
                print(f"   {url}: ❌ غير متاح")
        
        # 3. اختبار قاعدة البيانات
        print("\n3. اختبار اتصال قاعدة البيانات...")
        try:
            import database as db
            candidates = db.get_all_candidates()
            print(f"   قاعدة البيانات: ✅ متصلة ({len(candidates)} مرشح)")
        except Exception as e:
            print(f"   قاعدة البيانات: ❌ {str(e)[:100]}")
        
        process.terminate()
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

if __name__ == '__main__':
    test_current_system()