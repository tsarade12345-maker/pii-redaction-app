# Deployment Guide for PII Redaction WebApp

This guide covers multiple deployment options for the PII Redaction WebApp.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### For Local Development
- Python 3.11+
- Node.js 18+
- Tesseract OCR installed
- Poppler installed (for PDF processing)

### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

## Local Development Deployment

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd PII-Redaction-WebApp/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Install system dependencies:**
   - **Windows:** 
     - Install Tesseract: `winget install --id UB-Mannheim.TesseractOCR`
     - Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
   - **Linux:**
     ```bash
     sudo apt-get update
     sudo apt-get install tesseract-ocr poppler-utils
     ```
   - **macOS:**
     ```bash
     brew install tesseract poppler
     ```

6. **Run the backend:**
   ```bash
   python app.py
   ```
   Backend will start on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd PII-Redaction-WebApp/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file (optional):**
   ```env
   REACT_APP_API_URL=http://localhost:5000
   ```

4. **Run the frontend:**
   ```bash
   npm start
   ```
   Frontend will start on `http://localhost:3000`

## Docker Deployment

### Quick Start with Docker Compose

1. **Navigate to project root:**
   ```bash
   cd PII-Redaction-WebApp
   ```

2. **Build and start containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/health

4. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

5. **Stop containers:**
   ```bash
   docker-compose down
   ```

### Individual Docker Builds

#### Backend Only

```bash
cd PII-Redaction-WebApp/backend
docker build -t pii-backend .
docker run -p 5000:5000 -v $(pwd)/redacted_documents:/app/redacted_documents pii-backend
```

#### Frontend Only

```bash
cd PII-Redaction-WebApp/frontend
docker build -t pii-frontend --build-arg REACT_APP_API_URL=http://localhost:5000 .
docker run -p 3000:80 pii-frontend
```

## Cloud Deployment Options

### Option 1: AWS Deployment

#### Using AWS Elastic Beanstalk (Backend)

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB:**
   ```bash
   cd backend
   eb init -p python-3.11 pii-redaction-app
   eb create pii-redaction-env
   ```

3. **Deploy:**
   ```bash
   eb deploy
   ```

#### Using AWS Amplify (Frontend)

1. Connect your repository to AWS Amplify
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm install
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: build
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

### Option 2: Azure Deployment

#### Backend (Azure App Service)

1. **Create App Service:**
   ```bash
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name pii-backend --runtime "PYTHON:3.11"
   ```

2. **Deploy:**
   ```bash
   cd backend
   az webapp up --name pii-backend --resource-group myResourceGroup
   ```

#### Frontend (Azure Static Web Apps)

1. Use Azure Static Web Apps extension in VS Code
2. Or deploy via Azure Portal

### Option 3: Google Cloud Platform

#### Backend (Cloud Run)

1. **Create Dockerfile** (already created)
2. **Deploy:**
   ```bash
   gcloud run deploy pii-backend --source ./backend --platform managed --region us-central1
   ```

#### Frontend (Cloud Storage + Cloud CDN)

1. Build frontend: `npm run build`
2. Upload to Cloud Storage bucket
3. Configure Cloud CDN

### Option 4: Heroku Deployment

#### Backend

1. **Create `Procfile` in backend:**
   ```
   web: python app.py
   ```

2. **Create `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   heroku create pii-backend
   git push heroku main
   ```

#### Frontend

1. Use Heroku Buildpack for static sites
2. Or deploy to Netlify/Vercel (recommended for React apps)

### Option 5: DigitalOcean App Platform

1. Connect GitHub repository
2. Configure:
   - Backend: Python service
   - Frontend: Static site
3. Set environment variables
4. Deploy

## Environment Variables

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_HOST` | `0.0.0.0` | Host to bind Flask server |
| `FLASK_PORT` | `5000` | Port to run Flask server |
| `FLASK_ENV` | `production` | Flask environment (development/production) |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://127.0.0.1:5000` | Backend API URL |

**Note:** React environment variables must be prefixed with `REACT_APP_` to be accessible in the browser.

## Production Considerations

### Security

1. **Enable HTTPS:** Use reverse proxy (nginx/traefik) with SSL certificates
2. **CORS Configuration:** Update CORS settings in `app.py` for production
3. **Environment Variables:** Never commit secrets to version control
4. **Rate Limiting:** Implement rate limiting for API endpoints
5. **Input Validation:** Ensure all inputs are validated

### Performance

1. **Caching:** Implement caching for static assets
2. **CDN:** Use CDN for frontend assets
3. **Database:** Consider adding database for session management
4. **Load Balancing:** Use load balancer for high traffic

### Monitoring

1. **Health Checks:** Use `/health` endpoint for monitoring
2. **Logging:** Implement structured logging
3. **Error Tracking:** Use services like Sentry
4. **Metrics:** Monitor CPU, memory, and response times

## Troubleshooting

### Backend Issues

**Tesseract not found:**
- Ensure Tesseract is installed and in PATH
- On Windows, update path in `app.py` if needed

**Poppler not found:**
- Download Poppler and update path in `app.py`
- Or set `POPPLER_PATH` environment variable

**Port already in use:**
- Change port: `export FLASK_PORT=5001`
- Or kill process using the port

### Frontend Issues

**Cannot connect to backend:**
- Check `REACT_APP_API_URL` environment variable
- Ensure backend is running
- Check CORS settings

**Build fails:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (requires 18+)

### Docker Issues

**Build fails:**
- Check Docker version
- Clear Docker cache: `docker system prune -a`
- Check disk space

**Container won't start:**
- Check logs: `docker-compose logs`
- Verify environment variables
- Check port conflicts

## Additional Resources

- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues or questions, please open an issue in the repository.

