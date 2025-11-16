"""
Production WSGI entry point for the PII Redaction WebApp
Use with: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:application
"""
from app import app, socketio

# For production with gunicorn + eventlet, we need to wrap the app
# Flask-SocketIO works with eventlet workers in gunicorn
application = app

