"""
WSGI entry point for Gunicorn.
Use start command:  gunicorn wsgi:app
If the worker still fails to boot, Render logs will show the full Python traceback.
"""
import sys

try:
    from app import app
except Exception as e:
    import traceback
    sys.stderr.write("Worker failed to boot - exception during app load:\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise
