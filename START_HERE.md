# Quick Start Guide - What to Do After Deployment

## ⚠️ Virtualization Not Enabled?

If Docker Desktop shows "Virtualization support not detected", you have two options:

1. **Run Locally (Easier - Recommended):** See `RUN_LOCALLY.md` for instructions
2. **Enable Virtualization:** See `ENABLE_VIRTUALIZATION.md` for BIOS setup

---

## Option A: Using Docker (Requires Virtualization)

## Step 1: Navigate to Project Directory

Open PowerShell or Command Prompt and run:

```powershell
cd PII-Redaction-WebApp
```

## Step 2: Start the Application

### Option A: Using Docker Compose V2 (Newer Docker)
```powershell
docker compose up --build -d
```

### Option B: Using Docker Compose V1 (Legacy)
```powershell
docker-compose up --build -d
```

**What this does:**
- ✅ Builds both backend and frontend Docker images
- ✅ Starts both containers in detached mode (runs in background)
- ✅ Sets up networking between services
- ✅ Runs in production mode automatically

**Expected output:**
```
[+] Building ...
[+] Running 2/2
 ✔ Container pii-backend    Started
 ✔ Container pii-frontend  Started
```

## Step 3: Verify Containers are Running

```powershell
# Check container status
docker compose ps
# OR
docker-compose ps
```

You should see:
```
NAME            STATUS          PORTS
pii-backend     Up              0.0.0.0:5000->5000/tcp
pii-frontend    Up              0.0.0.0:3000->80/tcp
```

## Step 4: Check Logs (Optional)

```powershell
# View all logs
docker compose logs

# View backend logs only
docker compose logs backend

# View frontend logs only
docker compose logs frontend

# Follow logs in real-time (Ctrl+C to exit)
docker compose logs -f
```

## Step 5: Access the Application

### 🌐 Frontend (Web Interface)
Open your web browser and navigate to:
```
http://localhost:3000
```

You should see the PII Redaction WebApp interface.

### 🔌 Backend API
The backend API is available at:
```
http://localhost:5000
```

### ❤️ Health Check
Test if the backend is running properly:
```
http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "PII Redaction API"
}
```

## Step 6: Test the Application

1. **Open the frontend** at http://localhost:3000
2. **Upload a document:**
   - Click "Choose File" or drag & drop
   - Select a PDF or image (PNG, JPG, etc.)
   - Choose redaction level (Basic/Intermediate/Critical)
   - Click "Upload and Process"
3. **Try live transcription:**
   - Click the microphone button
   - Speak into your microphone
   - Watch for PII detection alerts
4. **Download redacted documents** after processing

## Common Commands

### Stop the Application
```powershell
docker compose down
# OR
docker-compose down
```

### Restart the Application
```powershell
docker compose restart
```

### Rebuild and Restart (after code changes)
```powershell
docker compose up --build -d
```

### View Container Status
```powershell
docker compose ps
```

### Stop and Remove Everything (including volumes)
```powershell
docker compose down -v
```

### View Resource Usage
```powershell
docker stats
```

## Troubleshooting

### ❌ "docker compose" command not found

**Solution:** You might need to use the legacy command:
```powershell
docker-compose up --build -d
```

Or install Docker Desktop which includes Docker Compose.

### ❌ Port Already in Use

**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution:** Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "5001:5000"  # Change backend port to 5001
  - "3001:80"    # Change frontend port to 3001
```

Then access at:
- Frontend: http://localhost:3001
- Backend: http://localhost:5001

### ❌ Containers Won't Start

1. **Check logs:**
   ```powershell
   docker compose logs
   ```

2. **Check Docker is running:**
   ```powershell
   docker ps
   ```

3. **Check disk space:**
   ```powershell
   docker system df
   ```

4. **Rebuild from scratch:**
   ```powershell
   docker compose down -v
   docker compose up --build
   ```

### ❌ Can't Access Frontend (localhost:3000)

1. **Verify frontend container is running:**
   ```powershell
   docker compose ps
   ```

2. **Check frontend logs:**
   ```powershell
   docker compose logs frontend
   ```

3. **Test if container is responding:**
   ```powershell
   curl http://localhost:3000
   ```

### ❌ Backend Not Responding

1. **Verify backend container is running:**
   ```powershell
   docker compose ps
   ```

2. **Check backend logs:**
   ```powershell
   docker compose logs backend
   ```

3. **Test health endpoint:**
   ```powershell
   curl http://localhost:5000/health
   ```
   Or open in browser: http://localhost:5000/health

### ❌ Build Fails

**Common issues:**
- **Out of disk space:** Free up space or run `docker system prune`
- **Network issues:** Check internet connection (needs to download images)
- **Docker not running:** Start Docker Desktop

**Solution:**
```powershell
# Clean up Docker
docker system prune -a

# Rebuild
docker compose up --build
```

## What's Running?

After successful deployment:

✅ **Backend (Flask + SocketIO)**
- Running on port 5000
- Using Gunicorn production server
- Health check: http://localhost:5000/health

✅ **Frontend (React)**
- Running on port 3000
- Served by Nginx
- Connects to backend automatically

✅ **Features Available:**
- Document upload (PDF, images)
- PII detection and redaction
- Live audio transcription
- Download redacted documents

## Next Steps

1. ✅ Application is running
2. ✅ Frontend accessible at http://localhost:3000
3. ✅ Backend API at http://localhost:5000
4. ✅ Ready to process documents!

**For production deployment**, see `PRODUCTION.md`

**For detailed deployment options**, see `DEPLOYMENT.md`
