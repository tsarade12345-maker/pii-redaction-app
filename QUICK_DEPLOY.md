# Quick Deploy Guide - Get Online in 10 Minutes! 🚀

## Easiest Method: Railway (Recommended)

### Prerequisites
- GitHub account
- Your code pushed to GitHub

### Step 1: Push to GitHub

If you haven't already:

```powershell
cd PII-Redaction-WebApp
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend (5 minutes)

1. **Go to Railway:** https://railway.app
2. **Sign up** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Click the service** that was created
7. **Go to Settings:**
   - Set **Root Directory** to: `PII-Redaction-WebApp/backend`
   - Set **Start Command** to: `gunicorn --config gunicorn_config.py wsgi:application`
8. **Go to Variables tab**, add:
   ```
   FLASK_ENV=production
   CORS_ORIGINS=*
   ```
9. **Copy the URL** (e.g., `https://pii-backend-production.up.railway.app`)

### Step 3: Deploy Frontend (5 minutes)

1. **In Railway, click "New Service"**
2. **Select "Deploy from GitHub repo"**
3. **Choose same repository**
4. **Click the new service**
5. **Go to Settings:**
   - Set **Root Directory** to: `PII-Redaction-WebApp/frontend`
   - Set **Build Command** to: `npm install && npm run build`
   - Set **Start Command** to: `npx serve -s build -l 3000`
6. **Go to Variables tab**, add:
   ```
   REACT_APP_API_URL=https://YOUR_BACKEND_URL.railway.app
   ```
   (Replace with your actual backend URL from Step 2)
7. **Copy the frontend URL**

### Step 4: Update CORS (Important!)

1. **Go back to backend service**
2. **Variables tab**
3. **Update CORS_ORIGINS:**
   ```
   CORS_ORIGINS=https://YOUR_FRONTEND_URL.railway.app
   ```
   (Replace with your actual frontend URL)

### Step 5: Test on Your Phone! 📱

1. Open the **frontend URL** on your phone's browser
2. Test uploading a document
3. Test live transcription

**Done!** 🎉

---

## Alternative: Render (Also Free)

### Backend on Render

1. Go to https://render.com
2. Sign up with GitHub
3. "New +" → "Web Service"
4. Connect repository
5. Settings:
   - **Root Directory:** `PII-Redaction-WebApp/backend`
   - **Build:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start:** `gunicorn --config gunicorn_config.py wsgi:application`
6. Add environment variables:
   - `FLASK_ENV=production`
   - `CORS_ORIGINS=https://your-frontend.onrender.com`

### Frontend on Render

1. "New +" → "Static Site"
2. Connect repository
3. Settings:
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Build:** `npm install && npm run build`
   - **Publish:** `build`
4. Environment variable:
   - `REACT_APP_API_URL=https://your-backend.onrender.com`

---

## Troubleshooting

### Build Fails
- Check logs in Railway/Render dashboard
- Verify all files are committed to GitHub

### Frontend Can't Connect
- Verify `REACT_APP_API_URL` matches backend URL exactly
- Check CORS settings include frontend URL

### Backend Crashes
- Check logs for errors
- Verify all environment variables are set
- Check if Tesseract/Poppler are needed (may need custom build)

---

## Need Help?

1. Check deployment logs in Railway/Render dashboard
2. Test backend health: `https://your-backend-url/health`
3. Check browser console for frontend errors

**You're all set!** Open the frontend URL on your phone and start using the app! 🎉

