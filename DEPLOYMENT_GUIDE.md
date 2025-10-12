# 🚀 Deployment Guide - Price Forecast API

This guide will walk you through deploying your Price Forecast API to Render.com (free tier available).

## 📋 Prerequisites

- [ ] GitHub account
- [ ] Render.com account (free)
- [ ] Git installed on your computer
- [ ] Your API tested locally and working

## 🎯 Quick Deployment Checklist

- [x] ✅ `requirements.txt` created
- [x] ✅ `main.py` ready
- [x] ✅ `render.yaml` configured
- [x] ✅ `.gitignore` set up
- [x] ✅ API tested locally
- [ ] Push to GitHub
- [ ] Deploy on Render

---

## 📦 Step 1: Prepare Your Code for GitHub

### 1.1 Initialize Git Repository (if not done)

Open your terminal in the project folder:

```bash
cd C:\Users\Mischelle\price-forecast-api
git init
```

### 1.2 Add Files to Git

```bash
git add .
git status
```

**Review what will be committed:**
- ✅ main.py
- ✅ requirements.txt
- ✅ render.yaml
- ✅ .gitignore
- ✅ README.md
- ✅ All Pricing Daily.xlsx
- ❌ __pycache__ (ignored by .gitignore)
- ❌ .venv (ignored by .gitignore)

### 1.3 Commit Your Code

```bash
git commit -m "Initial commit: Price Forecast API with weekly forecasts"
```

---

## 🌐 Step 2: Create GitHub Repository

### Option A: Using GitHub Website

1. **Go to GitHub**
   - Visit https://github.com
   - Click "+" → "New repository"

2. **Repository Settings**
   - **Name**: `price-forecast-api`
   - **Description**: "Price forecasting API with weekly, daily, and extended forecasts"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README (we already have one)
   - Click "Create repository"

3. **Push Your Code**

   Copy the commands from GitHub and run them:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/price-forecast-api.git
   git branch -M main
   git push -u origin main
   ```

### Option B: Using GitHub Desktop

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose your project folder
4. Click "Publish repository"
5. Choose name and visibility
6. Click "Publish"

---

## 🚀 Step 3: Deploy on Render

### 3.1 Sign Up / Log In to Render

1. Go to https://render.com
2. Sign up using your GitHub account (recommended)
3. Authorize Render to access your GitHub repositories

### 3.2 Create New Web Service

1. **Click "New +"** → **"Web Service"**

2. **Connect Repository**
   - Find `price-forecast-api` in the list
   - Click "Connect"

3. **Configure Service**
   
   Render should auto-detect settings from `render.yaml`, but verify:
   
   - **Name**: `price-forecast-api` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free (or choose paid for better performance)

4. **Advanced Settings** (optional)
   
   Add environment variables if needed:
   - Key: `PYTHON_VERSION`
   - Value: `3.10.0`

5. **Create Web Service**
   - Click "Create Web Service"
   - Wait for deployment (5-15 minutes first time)

### 3.3 Monitor Deployment

Watch the logs in real-time:
- ✅ Installing dependencies...
- ✅ Building...
- ✅ Starting service...
- ✅ Live! 🎉

---

## ✅ Step 4: Test Your Deployed API

Once deployment is complete, you'll get a URL like:
```
https://price-forecast-api-xxxx.onrender.com
```

### Test Endpoints:

1. **Root Endpoint**
   ```
   https://your-app-name.onrender.com/
   ```
   Should return: `{"message": "Price Forecast API running!"}`

2. **Interactive Documentation**
   ```
   https://your-app-name.onrender.com/docs
   ```

3. **Get Commodities**
   ```
   https://your-app-name.onrender.com/commodities
   ```

4. **Weekly Forecast**
   ```
   https://your-app-name.onrender.com/forecast-weekly/rice/3
   ```

5. **Daily Forecast**
   ```
   https://your-app-name.onrender.com/forecast/rice/7
   ```

---

## 🔄 Step 5: Update Your Application

### When you make changes to your code:

1. **Test locally first**
   ```bash
   uvicorn main:app --reload
   ```

2. **Commit changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

3. **Auto-deploy**
   - Render automatically detects the push
   - Rebuilds and redeploys your API
   - Takes 2-5 minutes

---

## 📱 Step 6: Use in Your Applications

### Update your app's API URL:

**JavaScript/React:**
```javascript
const API_URL = "https://your-app-name.onrender.com";

async function getWeeklyForecast(commodity, months = 3) {
  const response = await fetch(`${API_URL}/forecast-weekly/${commodity}/${months}`);
  return await response.json();
}
```

**React Native:**
```javascript
const API_URL = "https://your-app-name.onrender.com";

fetch(`${API_URL}/forecast-weekly/rice/3`)
  .then(res => res.json())
  .then(data => console.log(data));
```

**Python:**
```python
import requests

API_URL = "https://your-app-name.onrender.com"

response = requests.get(f"{API_URL}/forecast-weekly/rice/3")
data = response.json()
```

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier:**
- ✅ Free forever
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes 30-60 seconds (cold start)
- ⚠️ 750 hours/month (enough for hobby projects)

### Solutions for Cold Starts:

1. **Use a ping service** (free):
   - UptimeRobot: https://uptimerobot.com
   - Ping your API every 10 minutes
   - Keeps service warm

2. **Upgrade to Paid Plan** ($7/month):
   - No spin-down
   - Always fast
   - Better for production

### Data Persistence

**Important:** Your Excel file is included in the deployment. To update data:

1. Replace `All Pricing Daily.xlsx` locally
2. Commit and push changes
3. Render will redeploy with new data

---

## 🛠️ Troubleshooting

### Issue: Build Failed

**Check:**
- All dependencies in `requirements.txt`
- Python version compatibility
- Review build logs in Render dashboard

**Solution:**
```bash
# Test locally first
pip install -r requirements.txt
python -m py_compile main.py
```

### Issue: Service Won't Start

**Check:**
- Start command is correct: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- `main.py` has `app = FastAPI()` at the top level
- No syntax errors

**Solution:**
- Review deploy logs
- Test locally: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Issue: 404 Not Found

**Check:**
- URL is correct
- Endpoint path matches your code
- Service is deployed (check dashboard)

### Issue: Slow Response (Cold Start)

**This is normal for free tier:**
- First request after 15 min: 30-60 seconds
- Subsequent requests: Fast (< 1 second)

**Solutions:**
- Use UptimeRobot to ping API every 10 min
- Upgrade to paid plan
- Show loading indicator in your app

### Issue: Excel File Not Found

**Check:**
- `All Pricing Daily.xlsx` is committed to Git
- File name matches exactly (case-sensitive)
- File is in the root directory

---

## 📊 Monitoring Your API

### Render Dashboard

Access at: https://dashboard.render.com

**Features:**
- 📈 View metrics (requests, response times)
- 📋 Read logs in real-time
- 🔄 Manual deploy triggers
- ⚙️ Environment variable management
- 📊 Usage statistics

### View Logs

```bash
# In Render dashboard → Your Service → Logs
# Or use Render CLI:
render logs -s price-forecast-api
```

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Root endpoint returns success message
- [ ] `/docs` shows interactive documentation
- [ ] `/commodities` returns list of commodities
- [ ] `/forecast/rice/7` returns 7-day forecast
- [ ] `/forecast-weekly/rice/3` returns 13 weeks of data
- [ ] API URL saved in your application
- [ ] Cold start behavior understood
- [ ] Update process documented for your team

---

## 📞 Support Resources

**Render Documentation:**
- https://render.com/docs/web-services

**FastAPI Documentation:**
- https://fastapi.tiangolo.com/deployment/

**Your API Documentation:**
- `README.md` - Full API reference
- `/docs` endpoint - Interactive testing

---

## 🎓 Next Steps

1. **Add custom domain** (optional)
   - Render Dashboard → Settings → Custom Domains
   - Point your domain to Render

2. **Enable monitoring**
   - Set up UptimeRobot for availability monitoring
   - Configure alerts for downtime

3. **Secure your API** (optional)
   - Add API key authentication
   - Limit CORS to specific domains
   - Rate limiting

4. **Scale up**
   - Upgrade plan when needed
   - Add caching (Redis)
   - Implement database for larger datasets

---

## ✨ Congratulations!

Your Price Forecast API is now live and accessible worldwide! 🎉

**Your deployed API:**
```
https://your-app-name.onrender.com
```

**Share it with:**
- Your team
- Your applications
- Your users

**Remember:**
- Test locally before pushing
- Monitor your free tier hours
- Keep your Excel data updated

Happy forecasting! 📈

