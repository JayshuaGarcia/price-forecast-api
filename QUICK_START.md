# ⚡ Quick Start Guide

Get your Price Forecast API running in 5 minutes!

## 🎯 What You Have

✅ A working FastAPI application  
✅ Weekly forecast endpoint (NEW!)  
✅ Daily forecast endpoint  
✅ Extended forecast (up to 24 months)  
✅ 11 commodities with historical data  
✅ All deployment files ready  

---

## 🚀 Option 1: Run Locally (Right Now!)

Your API is already running! 🎉

**Access it at:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

**Try these URLs in your browser:**

1. **Get all commodities:**
   ```
   http://localhost:8000/commodities
   ```

2. **Weekly forecast for rice (3 months):**
   ```
   http://localhost:8000/forecast-weekly/rice/3
   ```

3. **Daily forecast for rice (7 days):**
   ```
   http://localhost:8000/forecast/rice/7
   ```

**To restart the server:**
```bash
cd C:\Users\Mischelle\price-forecast-api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📱 Option 2: Use from Your App (Local Network)

### Find your IP address:

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Your app should use:**
```
http://YOUR_IP:8000/forecast-weekly/rice/3
```

**Example:**
```javascript
// React Native
fetch('http://192.168.1.100:8000/forecast-weekly/rice/3')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🌐 Option 3: Deploy to Internet (Render.com)

### Step-by-Step:

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Price Forecast API"
   git remote add origin YOUR_GITHUB_URL
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - Sign in with GitHub
   - New + → Web Service
   - Connect your repository
   - Click "Create Web Service"
   - Wait 5-10 minutes ☕

3. **Get your URL:**
   ```
   https://price-forecast-api-xxxx.onrender.com
   ```

**📖 Full deployment guide:** See `DEPLOYMENT_GUIDE.md`

---

## 🧪 Test Your API

**Run the test script:**
```bash
python test_api.py
```

This will test:
- ✅ Get commodities
- ✅ Daily forecast
- ✅ Weekly forecast

---

## 📊 API Endpoints Cheat Sheet

| Endpoint | Example | What it does |
|----------|---------|--------------|
| `/commodities` | `GET /commodities` | List all commodities |
| `/forecast/{commodity}/{days}` | `GET /forecast/rice/30` | Daily forecast (1-365 days) |
| `/forecast-weekly/{commodity}/{months}` | `GET /forecast-weekly/rice/3` | Weekly forecast (1-12 months) |
| `/extended-forecast/{commodity}/{months}` | `GET /extended-forecast/rice/12` | Extended forecast (1-24 months) |
| `/commodity/{commodity}` | `GET /commodity/rice` | Commodity details & stats |
| `/history` | `GET /history` | All historical data |

---

## 💻 Integration Examples

### JavaScript (Web App)
```javascript
const API_URL = "http://localhost:8000";

async function getWeeklyForecast() {
  const response = await fetch(`${API_URL}/forecast-weekly/rice/3`);
  const data = await response.json();
  
  console.log(`Commodity: ${data.commodity}`);
  console.log(`Total Weeks: ${data.total_weeks}`);
  console.log(`Trend: ${data.overall_statistics.overall_trend}`);
  
  data.weekly_forecasts.forEach(week => {
    console.log(`Week ${week.week_number}: ₱${week.average_forecast}`);
  });
}

getWeeklyForecast();
```

### React
```jsx
import React, { useEffect, useState } from 'react';

function ForecastComponent() {
  const [forecast, setForecast] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/forecast-weekly/rice/3')
      .then(res => res.json())
      .then(data => setForecast(data));
  }, []);
  
  if (!forecast) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{forecast.commodity} - 3 Month Forecast</h1>
      <p>Trend: {forecast.overall_statistics.overall_trend}</p>
      {forecast.weekly_forecasts.map(week => (
        <div key={week.week_number}>
          <h3>Week {week.week_number}</h3>
          <p>₱{week.average_forecast}</p>
        </div>
      ))}
    </div>
  );
}
```

### Python
```python
import requests

response = requests.get('http://localhost:8000/forecast-weekly/rice/3')
data = response.json()

print(f"Commodity: {data['commodity']}")
print(f"Trend: {data['overall_statistics']['overall_trend']}")

for week in data['weekly_forecasts']:
    print(f"Week {week['week_number']}: ₱{week['average_forecast']}")
```

---

## 🎨 Example Response (Weekly Forecast)

```json
{
  "commodity": "rice",
  "forecast_period_months": 3,
  "total_weeks": 13,
  "weekly_forecasts": [
    {
      "week_number": 1,
      "month": 1,
      "week_label": "Week 1 (Month 1)",
      "date_range": "2025-10-13 to 2025-10-19",
      "start_date": "2025-10-13",
      "end_date": "2025-10-19",
      "average_forecast": 51.65,
      "min_forecast": 51.20,
      "max_forecast": 52.10,
      "days_in_week": 7
    }
  ],
  "overall_statistics": {
    "starting_price": 51.65,
    "ending_price": 51.20,
    "price_change": -0.45,
    "price_change_percent": -0.87,
    "overall_trend": "Decreasing",
    "average_price": 51.42,
    "min_weekly_avg": 51.20,
    "max_weekly_avg": 51.65
  }
}
```

---

## 📚 Documentation Files

- **`README.md`** - Complete API documentation
- **`DEPLOYMENT_GUIDE.md`** - Step-by-step deployment instructions
- **`QUICK_START.md`** - This file! Quick reference
- **Interactive Docs** - http://localhost:8000/docs

---

## ❓ Common Issues

### Server not running?
```bash
cd C:\Users\Mischelle\price-forecast-api
uvicorn main:app --reload
```

### Port already in use?
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then start on different port
uvicorn main:app --reload --port 3000
```

### Module not found?
```bash
pip install -r requirements.txt
```

### Can't connect from phone?
- Use your computer's IP address (not localhost)
- Make sure phone and computer are on same WiFi
- Check firewall settings

---

## 🎉 You're Ready!

Your API is working and ready to integrate into any application!

**Next steps:**
1. ✅ Test all endpoints using `/docs`
2. ✅ Integrate into your app
3. ✅ Deploy to Render (when ready)
4. ✅ Share with your team

**Need help?**
- Check `README.md` for detailed docs
- Use `/docs` for interactive testing
- Run `python test_api.py` to verify everything works

Happy coding! 🚀

