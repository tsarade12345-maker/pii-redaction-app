"""
Gunicorn configuration file for production deployment
"""
import multiprocessing
import os

# Server socket
# Use PORT from environment (Railway/Render/Heroku provide this)
port = int(os.getenv('PORT', '5000'))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = 1  # Flask-SocketIO requires 1 worker with eventlet
worker_class = "eventlet"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "pii-redaction-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

