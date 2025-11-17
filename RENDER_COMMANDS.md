# Render Build and Start Commands

## Build Command

```
pip install -r requirements.txt --constraint <(echo "--no-deps en-core-web-lg --no-deps en-core-web-sm") || pip install -r requirements.txt
```

**OR (simpler, recommended):**

```
pip install -r requirements.txt
```

**What this does:**
- Installs all Python packages from requirements.txt
- Note: spaCy model is optional - the app will work without it using default AnalyzerEngine
- If presidio-analyzer installs spacy, that's fine - but models are NOT needed
- The app will work without spaCy models using default AnalyzerEngine

## Start Command

```
gunicorn --config gunicorn_config.py wsgi:application
```

**What this does:**
- Starts the Flask app using Gunicorn production server
- Uses the gunicorn_config.py configuration file
- Runs the WSGI application from wsgi.py

## Important Notes

- **Root Directory** should be: `backend`
- These commands run from the `backend` directory automatically
- Make sure both commands are set correctly in Render settings

