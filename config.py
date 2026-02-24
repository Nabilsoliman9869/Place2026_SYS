# [file name]: config.py
"""
إعدادات نظام الموارد البشرية
"""

import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).parent.absolute()
LOG_DIR = BASE_DIR / 'logs'
BACKUP_DIR = BASE_DIR / 'backups'
UPLOAD_DIR = BASE_DIR / 'uploads'

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [LOG_DIR, BACKUP_DIR, UPLOAD_DIR]:
    directory.mkdir(exist_ok=True)

# إعدادات قاعدة البيانات
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': '.',  # استخدام النقطة للمخدم المحلي
    'port': '1477',  # المنفذ المحدد في app.py
    'database': 'Place2026',
    'username': 'sa',
    'password': '123',
    'timeout': 30,
    'autocommit': False
}

# سلسلة الاتصال
def get_connection_string():
    config = DATABASE_CONFIG
    return (
        f"DRIVER={{{config['driver']}}};"
        f"SERVER={config['server']},{config['port']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']};"
        f"Charset=UTF8;"
    )

# إعدادات التطبيق
APP_CONFIG = {
    'name': 'نظام إدارة التدريب والموارد البشرية',
    'version': '2.0.0',
    'debug': True,
    'host': '0.0.0.0',
    'port': 5000,
    'secret_key': 'hr-system-secret-key-change-in-production',
    'session_timeout': 24,  # ساعات
    'items_per_page': 20
}

# إعدادات التسجيل
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'app.log',
            'formatter': 'standard'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# إعدادات البريد الإلكتروني (اختياري)
EMAIL_CONFIG = {
    'enabled': False,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': '',
    'sender_password': '',
    'admin_email': 'admin@example.com'
}

# إعدادات QR Code
QR_CONFIG = {
    'version': 1,
    'box_size': 10,
    'border': 4,
    'fill_color': '#1a237e',
    'back_color': 'white'
}

# إعدادات النسخ الاحتياطي
BACKUP_CONFIG = {
    'enabled': True,
    'keep_days': 7,
    'backup_time': '02:00',  # 2 صباحاً
    'compress': True
}

# إعدادات الأمان
SECURITY_CONFIG = {
    'password_min_length': 8,
    'password_require_uppercase': True,
    'password_require_lowercase': True,
    'password_require_numbers': True,
    'max_login_attempts': 5,
    'lockout_time': 15  # دقائق
}

# أدوار المستخدمين
USER_ROLES = {
    'admin': {
        'name': 'مدير النظام',
        'permissions': ['all']
    },
    'manager': {
        'name': 'مدير',
        'permissions': ['view', 'edit', 'delete', 'report']
    },
    'agent': {
        'name': 'وكيل',
        'permissions': ['view', 'edit']
    },
    'viewer': {
        'name': 'مشاهد',
        'permissions': ['view']
    }
}

# حالات المرشحين
CANDIDATE_STATUSES = {
    'new': 'جديد',
    'contacted': 'تم الاتصال',
    'interviewed': 'تمت المقابلة',
    'trained': 'تم التدريب',
    'hired': 'تم التوظيف',
    'rejected': 'مرفوض',
    'archived': 'مؤرشف'
}

# حالات تسجيلات الاهتمام
INTEREST_STATUSES = {
    'new': 'جديد',
    'contacted': 'تم الاتصال',
    'registered': 'تم التسجيل',
    'converted': 'تم التحويل',
    'not_interested': 'غير مهتم',
    'invalid': 'غير صالح'
}

print(f"✅ تم تحميل إعدادات: {APP_CONFIG['name']} v{APP_CONFIG['version']}")