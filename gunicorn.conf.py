import os
import multiprocessing

# Worker configuration - SAFE with pyodbc
# Use sync workers (not gevent) - multiple workers handle concurrent requests
workers = int(os.environ.get('WEB_CONCURRENCY',
                             min(multiprocessing.cpu_count() * 2, 4)))

worker_class = 'sync'  # Safe with pyodbc (not gevent)
worker_connections = 1000  # Max concurrent connections per worker

# Timeout settings
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))  # 120s for slow SQL queries
keepalive = 5

# Worker recycling - prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Don't preload app (safer with database connections)
preload_app = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
