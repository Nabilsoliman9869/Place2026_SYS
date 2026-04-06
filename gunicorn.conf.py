"""
Gunicorn configuration for Place2026_SYS (Flask / SQL Server).

Key goals:
  - Async gevent workers to handle concurrent requests without blocking.
  - Connection keep-alive to reduce TCP handshake overhead.
  - Automatic worker recycling to prevent memory leaks over long runs.
  - Hard request timeout so a slow SQL Server query never hangs a worker
    indefinitely.
"""

import multiprocessing

# ---------------------------------------------------------------------------
# Worker count & class
# ---------------------------------------------------------------------------
# 2-4× CPU cores is the standard recommendation for I/O-bound workloads.
# We cap at 4 so a small Railway instance isn't overwhelmed.
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)

# gevent turns each sync worker into an async coroutine pool, allowing
# hundreds of concurrent in-flight requests per worker without threads.
worker_class = "gevent"

# Maximum simultaneous greenlets per worker.  1 000 is a safe default for
# a DB-heavy app; raise if you see "too many open connections" errors.
worker_connections = 1000

# ---------------------------------------------------------------------------
# Timeouts & keep-alive
# ---------------------------------------------------------------------------
# Kill a worker that hasn't responded within 30 s.  This prevents a single
# slow SQL Server query from blocking a worker slot forever.
timeout = 30

# Keep the TCP connection open for 5 s after a response so the next request
# from the same client reuses it (reduces latency for browser users).
keepalive = 5

# ---------------------------------------------------------------------------
# Worker recycling (memory leak prevention)
# ---------------------------------------------------------------------------
# Restart a worker after it has served this many requests …
max_requests = 1000
# … plus a random jitter so all workers don't restart simultaneously.
max_requests_jitter = 100

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
accesslog = "-"   # stdout — Railway captures this automatically
errorlog  = "-"   # stderr
loglevel  = "info"
