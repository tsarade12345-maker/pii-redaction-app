# Quick Start Guide

Get the PII Redaction WebApp running in minutes!

## Option 1: Docker (Easiest) 🐳

**Prerequisites:** Docker and Docker Compose installed

```bash
# Navigate to project directory
cd PII-Redaction-WebApp

# Start the application
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

That's it! The app is now running.

## Option 2: Local Development

### Backend

```bash
cd PII-Redaction-WebApp/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Install Tesseract OCR
# Windows: winget install --id UB-Mannheim.TesseractOCR
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# Run backend
python app.py
```

### Frontend

```bash
cd PII-Redaction-WebApp/frontend

# Install dependencies
npm install

# Run frontend
npm start
```

## Troubleshooting

**Port already in use?**
- Change backend port: Set `FLASK_PORT=5001` environment variable
- Change frontend port: `PORT=3001 npm start`

**Docker build fails?**
- Ensure Docker is running
- Check disk space: `docker system df`
- Clear cache: `docker system prune -a`

**Can't connect frontend to backend?**
- Check backend is running on port 5000
- Verify `REACT_APP_API_URL` in frontend `.env` file
- Check browser console for CORS errors

For more details, see [DEPLOYMENT.md](./DEPLOYMENT.md)

