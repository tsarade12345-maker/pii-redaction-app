# 🚀 Deploy Now - Step by Step Guide

Follow these steps to deploy your app online in 15 minutes!

## ✅ Pre-Deployment Checklist

- [x] All deployment files created
- [x] Backend configured for production
- [x] Frontend configured for production
- [ ] Code pushed to GitHub
- [ ] Deployed to cloud platform

---

## Step 1: Initialize Git Repository

Open PowerShell in the project root and run:

```powershell
cd C:\Users\Admin\Desktop\Arrancars_AB2_10-main\PII-Redaction-WebApp
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

---

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (name it `pii-redaction-app` or similar)
3. **DO NOT** initialize with README
4. Copy the repository URL

---

## Step 3: Push to GitHub

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details.

---

## Step 4: Deploy to Railway (Easiest Method)

### 4a. Deploy Backend

1. **Go to:** https://railway.app
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Authorize Railway** to access your GitHub
5. **Select your repository**
6. **Click on the service** that appears
7. **Go to Settings tab:**
   - **Root Directory:** `PII-Redaction-WebApp/backend`
   - **Start Command:** `gunicorn --config gunicorn_config.py wsgi:application`
8. **Go to Variables tab**, click "New Variable" and add:
   - Name: `FLASK_ENV` → Value: `production`
   - Name: `CORS_ORIGINS` → Value: `*` (we'll update this later)
9. **Wait for deployment** (2-3 minutes)
10. **Copy the URL** from the service (e.g., `https://pii-backend-production.up.railway.app`)

### 4b. Deploy Frontend

1. **In Railway dashboard, click "+ New"**
2. **Select "GitHub Repo"**
3. **Choose the same repository**
4. **Click on the new service**
5. **Go to Settings tab:**
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npx serve -s build -l 3000`
6. **Go to Variables tab**, add:
   - Name: `REACT_APP_API_URL` → Value: `https://YOUR_BACKEND_URL.railway.app`
     (Replace with the backend URL from step 4a)
7. **Wait for deployment** (2-3 minutes)
8. **Copy the frontend URL**

### 4c. Update CORS

1. **Go back to backend service**
2. **Variables tab**
3. **Edit `CORS_ORIGINS`** variable:
   - Change value to: `https://YOUR_FRONTEND_URL.railway.app`
   - (Use the frontend URL from step 4b)
4. **Backend will automatically redeploy**

---

## Step 5: Test Your Deployment! 📱

1. **Open the frontend URL** on your phone's browser
2. **Test uploading a document**
3. **Test live transcription** (grant microphone permission)

**🎉 Your app is now live and accessible from anywhere!**

---

## Alternative: Deploy to Render

If Railway doesn't work, try Render:

### Backend on Render:

1. Go to https://render.com
2. Sign up with GitHub
3. "New +" → "Web Service"
4. Connect repository
5. Settings:
   - **Name:** `pii-backend`
   - **Root Directory:** `PII-Redaction-WebApp/backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command:** `gunicorn --config gunicorn_config.py wsgi:application`
6. Environment Variables:
   - `FLASK_ENV=production`
   - `CORS_ORIGINS=https://your-frontend.onrender.com`
7. Click "Create Web Service"

### Frontend on Render:

1. "New +" → "Static Site"
2. Connect repository
3. Settings:
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
4. Environment Variable:
   - `REACT_APP_API_URL=https://your-backend.onrender.com`
5. Click "Create Static Site"

---

## Troubleshooting

### Build Fails
- Check logs in Railway/Render dashboard
- Verify all files are in the repository
- Check if Python/Node versions are correct

### Frontend Can't Connect
- Verify `REACT_APP_API_URL` is correct
- Check CORS settings include frontend URL
- Test backend health: `https://your-backend-url/health`

### Backend Crashes
- Check deployment logs
- Verify environment variables are set
- Check if Tesseract is needed (may require custom Dockerfile)

---

## Your URLs

After deployment, you'll have:
- **Backend:** `https://your-backend-url.railway.app`
- **Frontend:** `https://your-frontend-url.railway.app` ← **Use this on your phone!**

---

## Next Steps

1. ✅ Code is ready
2. ⏳ Push to GitHub
3. ⏳ Deploy to Railway/Render
4. ⏳ Test on your phone
5. 🎉 Share with others!

Good luck! 🚀

