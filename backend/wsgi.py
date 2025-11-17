"""
Production WSGI entry point for the PII Redaction WebApp
Use with: gunicorn --worker-class sync --threads 4 -w 1 --bind 0.0.0.0:5000 wsgi:application
"""
from app import app, socketio

# For production with gunicorn + threading mode
# Flask-SocketIO works with sync workers using threads in gunicorn
application = app

