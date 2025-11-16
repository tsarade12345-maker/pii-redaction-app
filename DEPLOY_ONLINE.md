# Deploy Online - Access from Your Phone

This guide will help you deploy the PII Redaction WebApp to the cloud so you can access it from any device, including your phone.

## Quick Comparison

| Platform | Free Tier | Ease | Best For |
|----------|-----------|------|----------|
| **Railway** | ✅ Yes | ⭐⭐⭐⭐⭐ | Easiest, all-in-one |
| **Render** | ✅ Yes | ⭐⭐⭐⭐ | Good free tier |
| **Heroku** | ❌ No | ⭐⭐⭐ | Simple but paid |
| **Vercel + Railway** | ✅ Yes | ⭐⭐⭐⭐ | Best performance |

## Option 1: Railway (Recommended - Easiest) 🚂

Railway is the easiest option with a free tier and automatic deployments.

### Step 1: Prepare for Railway

1. **Create `railway.json` in project root:**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --config backend/gunicorn_config.py wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Create `Procfile` in backend folder:**

```
web: gunicorn --config gunicorn_config.py wsgi:application
```

3. **Create `runtime.txt` in backend folder:**

```
python-3.11.0
```

### Step 2: Deploy Backend

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Select your repository
6. Railway will auto-detect it's a Python app
7. Set root directory to `PII-Redaction-WebApp/backend`
8. Add environment variables:
   ```
   FLASK_ENV=production
   PORT=5000
   CORS_ORIGINS=https://your-frontend-url.railway.app
   ```
9. Railway will automatically build and deploy

### Step 3: Deploy Frontend

1. In Railway, click "New Service"
2. Select "Deploy from GitHub repo"
3. Select same repository
4. Set root directory to `PII-Redaction-WebApp/frontend`
5. Add build command: `npm install && npm run build`
6. Add start command: `npx serve -s build -l 3000`
7. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend-url.railway.app
   ```

### Step 4: Get Your URLs

1. Railway will give you URLs like:
   - Backend: `https://pii-backend-production.up.railway.app`
   - Frontend: `https://pii-frontend-production.up.railway.app`

2. Update frontend environment variable with backend URL

3. Access from your phone: Open the frontend URL!

---

## Option 2: Render (Free Tier Available) 🎨

### Step 1: Deploy Backend

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** `pii-backend`
   - **Root Directory:** `PII-Redaction-WebApp/backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command:** `gunicorn --config gunicorn_config.py wsgi:application`
6. Add environment variables:
   ```
   FLASK_ENV=production
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```
7. Click "Create Web Service"

### Step 2: Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `pii-frontend`
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
4. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```
5. Click "Create Static Site"

### Step 3: Access from Phone

- Frontend URL: `https://pii-frontend.onrender.com`
- Open this URL on your phone!

---

## Option 3: Vercel (Frontend) + Railway (Backend) ⚡

Best performance option - Vercel for frontend, Railway for backend.

### Backend on Railway

Follow Option 1, Step 2 above.

### Frontend on Vercel

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Import your repository
5. Configure:
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Framework Preset:** Create React App
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
6. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend-url.railway.app
   ```
7. Click "Deploy"

Vercel will give you a URL like: `https://pii-redaction.vercel.app`

---

## Option 4: Heroku (Paid, but Simple) 💜

### Step 1: Install Heroku CLI

```powershell
winget install Heroku.HerokuCLI
```

### Step 2: Login

```powershell
heroku login
```

### Step 3: Deploy Backend

```powershell
cd PII-Redaction-WebApp\backend
heroku create pii-backend-yourname
heroku config:set FLASK_ENV=production
git push heroku main
```

### Step 4: Deploy Frontend

```powershell
cd ..\frontend
heroku create pii-frontend-yourname --buildpack https://github.com/mars/create-react-app-buildpack.git
heroku config:set REACT_APP_API_URL=https://pii-backend-yourname.herokuapp.com
git push heroku main
```

---

## Important: Update CORS Settings

After deployment, update your backend CORS to allow your frontend domain:

**In Railway/Render/Heroku environment variables:**
```
CORS_ORIGINS=https://your-frontend-url.com,https://your-frontend-url.railway.app
```

**Or for multiple domains:**
```
CORS_ORIGINS=https://frontend1.com,https://frontend2.com
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible (test `/health` endpoint)
- [ ] Frontend is accessible
- [ ] Frontend can connect to backend (check browser console)
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] Test upload functionality
- [ ] Test on your phone!

---

## Testing on Your Phone

1. Get your frontend URL (e.g., `https://pii-frontend.railway.app`)
2. Open the URL in your phone's browser
3. Test uploading a document
4. Test live transcription (if microphone permissions are granted)

---

## Troubleshooting

### Backend Not Starting

- Check logs in Railway/Render dashboard
- Verify all environment variables are set
- Check if Tesseract/Poppler dependencies are needed (may need custom Dockerfile)

### Frontend Can't Connect to Backend

- Verify `REACT_APP_API_URL` is correct
- Check CORS settings in backend
- Test backend URL directly in browser

### Build Fails

- Check build logs
- Verify all dependencies are in `requirements.txt` and `package.json`
- Ensure Python/Node versions are compatible

### 404 Errors

- Verify root directories are set correctly
- Check if build output directory is correct

---

## Recommended: Railway (Easiest)

For your use case, **Railway is recommended** because:
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Easy to set up
- ✅ Good documentation
- ✅ Works well for both frontend and backend

---

## Next Steps

1. Choose a platform (Railway recommended)
2. Follow the deployment steps above
3. Get your URLs
4. Test on your phone!
5. Share the URL with others if needed

Good luck with your deployment! 🚀

