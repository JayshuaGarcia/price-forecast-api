# 🚀 UptimeRobot Setup Guide - Keep Your API Alive 24/7

## Why UptimeRobot?
- ✅ **Free forever** (50 monitors)
- ✅ **Keeps your API awake** 24/7
- ✅ **5-minute intervals** (perfect for free Render)
- ✅ **No credit card required**

## 📋 Step-by-Step Setup

### 1. **Go to UptimeRobot**
- Visit: https://uptimerobot.com
- Click **"Sign Up"** (free account)

### 2. **Create Your Account**
- Use your email
- Choose a password
- **No credit card needed!**

### 3. **Add a New Monitor**
- Click **"+ Add New Monitor"**
- Select **"HTTP(s)"**

### 4. **Configure Your Monitor**
```
Monitor Type: HTTP(s)
Friendly Name: Price Forecast API
URL: https://price-forecast-api.onrender.com/
Monitoring Interval: 5 minutes
```

### 5. **Advanced Settings**
- **Monitor Timeout**: 30 seconds
- **Keyword**: "Price Forecast API running!"
- **Alert Contacts**: Add your email

### 6. **Save and Activate**
- Click **"Create Monitor"**
- Your API will be pinged every 5 minutes!

## 🎯 What This Does

- **Pings your API** every 5 minutes
- **Keeps Render awake** (no more sleeping!)
- **Sends alerts** if API goes down
- **Free forever** (up to 50 monitors)

## ⚡ Alternative: Use the Keep-Alive Script

If you prefer to run your own keep-alive:

```bash
# Run this on your computer:
python keep_alive.py
```

This will ping your API every 5 minutes to keep it awake.

## 🔍 Test Your Setup

After setting up UptimeRobot:

1. **Wait 5-10 minutes** for first ping
2. **Test your API**:
   ```
   https://price-forecast-api.onrender.com/commodities
   ```
3. **Should respond instantly!**

## 📱 For React Native Testing

Once UptimeRobot is active, your React Native app will work perfectly:

```javascript
const API_URL = 'https://price-forecast-api.onrender.com';

// This will work instantly!
const response = await fetch(`${API_URL}/forecast-weekly/rice/3`);
```

## 🎉 Benefits

- ✅ **API always awake** (no more timeouts)
- ✅ **Instant responses** in your React Native app
- ✅ **Free monitoring** and alerts
- ✅ **24/7 availability** for your users

Your price forecast API will be production-ready! 🚀

