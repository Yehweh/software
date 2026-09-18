import os
import sys

raw_port = os.environ.get("PORT", "10000")
try:
    port = int(raw_port) if raw_port and raw_port.strip() else 10000
except (ValueError, TypeError):
    port = 10000

print(f"Starting server on 0.0.0.0:{port}...")

try:
    import gunicorn  # noqa: F401
    has_gunicorn = True
except ImportError:
    has_gunicorn = False

if has_gunicorn and os.name != "nt":
    cmd = f"gunicorn --bind 0.0.0.0:{port} --workers 2 --timeout 120 app:app"
    sys.exit(os.system(cmd))
else:
    from app import app
    app.run(host="0.0.0.0", port=port)
