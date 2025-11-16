# PII Redaction WebApp

A web application for identifying and redacting Personally Identifiable Information (PII) from documents and audio transcriptions.

## Features

- 📄 **Document Processing**: Upload PDFs and images (PNG, JPG, etc.)
- 🔍 **PII Detection**: Automatically detects various types of PII including:
  - Credit/Debit Card Numbers
  - Aadhaar Numbers
  - PAN Numbers
  - Passport Numbers
  - Driving License Numbers
  - Bank Account Numbers
  - IFSC Codes
  - UPI IDs
  - Phone Numbers
  - Email Addresses
- 🎤 **Live Audio Transcription**: Real-time speech-to-text with PII detection
- 🎚️ **Redaction Levels**: Basic, Intermediate, and Critical redaction levels
- 📥 **Download Redacted Documents**: Download processed documents with sensitive information redacted

## Tech Stack

### Backend
- Flask (Python web framework)
- Flask-SocketIO (WebSocket support)
- Tesseract OCR (Optical Character Recognition)
- Presidio (PII detection)
- OpenCV (Image processing)
- SpeechRecognition (Audio transcription)

### Frontend
- React 19
- Socket.IO Client (Real-time communication)
- Axios (HTTP client)

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd PII-Redaction-WebApp

# Start the application
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Local Development

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed setup instructions.

## Project Structure

```
PII-Redaction-WebApp/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend Docker configuration
│   └── utils/
│       └── pii_detector.py # PII detection utilities
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── Upload.js      # File upload component
│   │   └── ...
│   ├── package.json       # Node dependencies
│   ├── Dockerfile        # Frontend Docker configuration
│   └── nginx.conf        # Nginx configuration
├── docker-compose.yml     # Docker Compose configuration
└── DEPLOYMENT.md         # Deployment guide
```

## API Endpoints

- `POST /upload` - Upload and process documents
- `GET /download/<filename>` - Download redacted documents
- `GET /health` - Health check endpoint
- WebSocket events:
  - `start_transcription` - Start live audio transcription
  - `stop_transcription` - Stop transcription
  - `transcription_update` - Receive transcription updates
  - `pii_alert` - Receive PII detection alerts

## Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

Supported deployment options:
- Docker & Docker Compose
- AWS (Elastic Beanstalk, Amplify)
- Azure (App Service, Static Web Apps)
- Google Cloud Platform (Cloud Run)
- Heroku
- DigitalOcean

## Requirements

### System Dependencies
- Tesseract OCR
- Poppler (for PDF processing)

### Python Dependencies
See `backend/requirements.txt`

### Node Dependencies
See `frontend/package.json`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project was created for AB2 hackathon (PS ID: 10)

## Support

For deployment issues, see the [Troubleshooting](#troubleshooting) section in DEPLOYMENT.md.

