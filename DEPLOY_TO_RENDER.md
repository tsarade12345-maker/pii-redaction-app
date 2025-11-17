# 🎨 Deploy to Render (Free Tier Available)

Railway's free plan only allows databases. **Render** has a better free tier that supports web services!

## Step 1: Sign Up for Render

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account**
4. Authorize Render to access your repositories

---

## Step 2: Deploy Backend

1. In Render dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** if prompted
4. Select your repository: **`tsarade12345-maker/pii-redaction-app`**
5. Configure the service:
   - **Name:** `pii-backend` (or any name you like)
   - **Region:** Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch:** `main`
   - **Root Directory:** `PII-Redaction-WebApp/backend`
   - **Runtime:** `Python 3`
   - **Build Command:** 
     ```
     pip install -r requirements.txt
     ```
     **Note:** spaCy model download is removed to avoid memory issues. The app works without it.
   - **Start Command:** 
     ```
     gunicorn --config gunicorn_config.py wsgi:application
     ```
6. Scroll down to **"Environment Variables"** section:
   - Click **"Add Environment Variable"**
   - Add: `FLASK_ENV` = `production`
   - Add: `CORS_ORIGINS` = `*` (we'll update this after frontend is deployed)
7. Scroll down to **"Plan"** section:
   - Select **"Free"** plan
8. Click **"Create Web Service"**
9. Render will start building and deploying (takes 3-5 minutes)
10. **Copy the URL** when deployment completes (e.g., `https://pii-backend.onrender.com`)

---

## Step 3: Deploy Frontend

1. In Render dashboard, click **"New +"** button again
2. Select **"Static Site"**
3. Select your repository: **`tsarade12345-maker/pii-redaction-app`**
4. Configure the service:
   - **Name:** `pii-frontend` (or any name you like)
   - **Branch:** `main`
   - **Root Directory:** `PII-Redaction-WebApp/frontend`
   - **Build Command:** 
     ```
     npm install && npm run build
     ```
   - **Publish Directory:** `build`
5. Scroll down to **"Environment Variables"** section:
   - Click **"Add Environment Variable"**
   - Add: `REACT_APP_API_URL` = `https://YOUR_BACKEND_URL.onrender.com`
     (Replace with the actual backend URL from Step 2)
6. Click **"Create Static Site"**
7. Render will start building and deploying (takes 2-3 minutes)
8. **Copy the frontend URL** when deployment completes (e.g., `https://pii-frontend.onrender.com`)

---

## Step 4: Update CORS (Important!)

1. Go back to your **backend service** in Render
2. Go to **"Environment"** tab
3. Find the `CORS_ORIGINS` variable
4. Click **"Edit"** and change the value to your **frontend URL**:
   ```
   https://YOUR_FRONTEND_URL.onrender.com
   ```
   (Use the actual frontend URL from Step 3)
5. Click **"Save Changes"**
6. Render will automatically redeploy the backend

---

## Step 5: Test on Your Phone! 📱

1. Open the **frontend URL** on your phone's browser
2. The app should load
3. Test uploading a document
4. Test live transcription (grant microphone permission when prompted)

**🎉 Your app is now live and accessible from anywhere!**

---

## Important Notes About Render Free Tier

- ⚠️ **Free services spin down after 15 minutes of inactivity**
- ⚠️ **First request after spin-down takes ~30 seconds** (cold start)
- ⚠️ **Free tier has resource limits** (512MB RAM, 0.1 CPU)
- ✅ **No credit card required**
- ✅ **Free SSL certificates**
- ✅ **Custom domains supported**

For production use, consider upgrading to a paid plan ($7/month per service).

---

## Troubleshooting

### Backend Not Starting
- Check the **"Logs"** tab in Render
- Verify all environment variables are set correctly
- Make sure Root Directory is `PII-Redaction-WebApp/backend`
- Check if build completed successfully

### Frontend Can't Connect to Backend
- Verify `REACT_APP_API_URL` matches your backend URL exactly
- Check CORS settings include your frontend URL
- Test backend health: `https://your-backend-url.onrender.com/health`

### Build Fails
- Check the **"Logs"** tab for error messages
- Verify all files are in the GitHub repository
- Make sure Python/Node versions are compatible

### Slow Response Times
- Free tier services spin down after inactivity
- First request after spin-down is slow (cold start)
- Consider upgrading to paid plan for always-on service

---

## Your URLs

After deployment, you'll have:
- **Backend:** `https://pii-backend.onrender.com`
- **Frontend:** `https://pii-frontend.onrender.com` ← **Use this on your phone!**

---

## Quick Reference

- **Render Dashboard:** https://dashboard.render.com
- **Your Repository:** https://github.com/tsarade12345-maker/pii-redaction-app
- **Render Docs:** https://render.com/docs

Good luck! 🚀

