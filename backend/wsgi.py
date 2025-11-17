"""
Production WSGI entry point for the PII Redaction WebApp
Use with: gunicorn --worker-class sync --threads 4 -w 1 --bind 0.0.0.0:5000 wsgi:application
"""
import os

# Print environment info for debugging
print(f"🔧 PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
print(f"🔧 FLASK_ENV: {os.getenv('FLASK_ENV', 'NOT SET')}")

from app import app

# For production with gunicorn
application = app

print("✅ WSGI application loaded successfully")

