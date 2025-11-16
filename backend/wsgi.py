"""
Production WSGI entry point for the PII Redaction WebApp
Use with: gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:5000 wsgi:application
"""
from app import app, socketio

# For production with gunicorn + gevent, we need to wrap the app
# Flask-SocketIO works with gevent workers in gunicorn
application = app

