# إعدادات Gunicorn للإنتاج (Railway / Docker / VPS)
# workers متزامنة (sync) — متوافقة مع pyodbc؛ تجنّب gevent مع ODBC إلا بعد اختبار شامل.
import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
# Railway: ضبط WEB_CONCURRENCY في لوحة المتغيرات (مثلاً 2–4 حسب الذاكرة)
# حتى 512MB: اترك WEB_CONCURRENCY=1 إذا لزم؛ الافتراضي يعتمد على عدد الأنوية المتاحة للحاوية
_default_workers = max(1, min(multiprocessing.cpu_count() or 2, 4))
workers = int(os.environ.get("WEB_CONCURRENCY", os.environ.get("GUNICORN_WORKERS", str(_default_workers))))
worker_class = "sync"
worker_connections = 1000  # لـ sync لا يُستخدم؛ يبقى للتوثيق
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))
# إعادة تشغيل العامل بعد N طلبات لتفادي تسرّب ذاكرة طويل الأمد
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "800"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "100"))
# False: أسلم مع اتصالات DB عند fork (لا مشاركة مقابض قبل الطلب)
preload_app = os.environ.get("GUNICORN_PRELOAD", "").lower() in ("1", "true", "yes")
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
capture_output = True
