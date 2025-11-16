# Running Locally Without Docker

Since Docker requires virtualization support, you can run the application directly on your system using Python and Node.js.

## Prerequisites Check

✅ Python 3.10.3 - Installed  
✅ Node.js v18.18.0 - Installed

## Step 1: Install System Dependencies

### Install Tesseract OCR

**Windows:**
```powershell
winget install --id UB-Mannheim.TesseractOCR
```

Or download from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Poppler (for PDF processing)

Download from: https://github.com/oschwartz10612/poppler-windows/releases/

Extract and note the path (e.g., `C:\poppler\bin`)

## Step 2: Set Up Backend

```powershell
# Navigate to backend directory
cd PII-Redaction-WebApp\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Step 3: Configure Backend (if needed)

If Poppler is not in PATH, edit `app.py` and update the `poppler_paths` list around line 73-78 with your Poppler path.

## Step 4: Start Backend

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Run backend (development mode)
python app.py
```

Backend will start on `http://localhost:5000`

## Step 5: Set Up Frontend (New Terminal)

Open a **new PowerShell window**:

```powershell
# Navigate to frontend directory
cd C:\Users\Admin\Desktop\Arrancars_AB2_10-main\PII-Redaction-WebApp\frontend

# Install dependencies
npm install

# Create .env file (optional, defaults to localhost:5000)
# Create a file named .env with:
# REACT_APP_API_URL=http://localhost:5000

# Start frontend
npm start
```

Frontend will start on `http://localhost:3000` and open automatically in your browser.

## Step 6: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

## Troubleshooting

### Tesseract Not Found
- Ensure Tesseract is installed and in PATH
- Or update the path in `app.py` (lines 28-31)

### Poppler Not Found
- Download Poppler and extract it
- Update the path in `app.py` (lines 73-78)

### Port Already in Use
- Change backend port: Set environment variable `FLASK_PORT=5001`
- Change frontend port: `set PORT=3001 && npm start`

### Module Not Found Errors
- Make sure virtual environment is activated: `.\venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Quick Start Script

Create a file `start-backend.ps1` in the backend folder:

```powershell
.\venv\Scripts\activate
python app.py
```

Create a file `start-frontend.ps1` in the frontend folder:

```powershell
npm start
```

Then run both in separate terminals.

