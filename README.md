# 📊 Price Forecast API

A FastAPI-based REST API for forecasting commodity prices using historical data. Supports daily, weekly, and extended forecasts with multiple time horizons.

## 🚀 Features

- **Daily Forecasts**: Predict prices for 1-365 days
- **Weekly Forecasts**: Get weekly summaries for up to 12 months
- **Extended Forecasts**: Long-term predictions up to 24 months
- **Multiple Forecasting Methods**: Prophet and enhanced linear models
- **Historical Data Access**: Query past pricing data
- **Commodity Statistics**: Get detailed statistics for any commodity
- **RESTful API**: Easy integration with any application

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Local Setup

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## 🌐 API Endpoints

### 📈 **Forecasting Endpoints**

#### 1. Daily Forecast
```http
GET /forecast/{commodity}/{days}
```
**Parameters:**
- `commodity`: Name of the commodity (e.g., "rice", "corn")
- `days`: Number of days to forecast (1-365)

**Example:**
```bash
GET /forecast/rice/30
```

**Response:**
```json
{
  "commodity": "rice",
  "forecast": [
    {
      "ds": "2025-10-13",
      "yhat": 51.65,
      "yhat_lower": 51.20,
      "yhat_upper": 52.10
    }
  ],
  "method": "simple_linear"
}
```

#### 2. Weekly Forecast (NEW!)
```http
GET /forecast-weekly/{commodity}/{months}
```
**Parameters:**
- `commodity`: Name of the commodity
- `months`: Number of months (1-12)

**Example:**
```bash
GET /forecast-weekly/rice/3
```

**Response:**
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
      "days_in_week": 7,
      "daily_forecasts": [...]
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

#### 3. Extended Forecast
```http
GET /extended-forecast/{commodity}/{months}
```
**Parameters:**
- `commodity`: Name of the commodity
- `months`: Number of months (1-24)

**Example:**
```bash
GET /extended-forecast/rice/12
```

#### 4. Forecast Summary
```http
GET /forecast-summary/{commodity}
```
Get short-term, medium-term, and long-term forecasts in one call.

**Example:**
```bash
GET /forecast-summary/rice
```

### 📊 **Data Endpoints**

#### 5. Get All Commodities
```http
GET /commodities
```

**Response:**
```json
{
  "commodities": ["rice", "corn", "sugar", ...]
}
```

#### 6. Get Historical Data
```http
GET /history
```
Returns all historical pricing data.

#### 7. Get Recent History
```http
GET /history/recent
```
Returns the last 1000 records.

#### 8. Get Commodity Details
```http
GET /commodity/{commodity}
```

**Example:**
```bash
GET /commodity/rice
```

**Response:**
```json
{
  "commodity": "rice",
  "total_records": 5234,
  "date_range": {
    "earliest": "2020-01-01",
    "latest": "2025-10-12"
  },
  "price_stats": {
    "min": 35.50,
    "max": 65.00,
    "avg": 48.75,
    "median": 49.00
  },
  "types": ["Type A", "Type B"]
}
```

#### 9. Get Data Statistics
```http
GET /data-stats
```
Get overall statistics for all commodities.

#### 10. Get All Data for a Commodity
```http
GET /commodity/{commodity}/all-data
```

#### 11. Get Data by Date Range
```http
GET /data/date-range/{start_date}/{end_date}
```

**Example:**
```bash
GET /data/date-range/2025-01-01/2025-03-31
```

## 💻 Integration Examples

### JavaScript/TypeScript
```javascript
// Fetch weekly forecast
async function getWeeklyForecast(commodity, months = 3) {
  const response = await fetch(
    `http://localhost:8000/forecast-weekly/${commodity}/${months}`
  );
  const data = await response.json();
  return data;
}

// Example usage
const forecast = await getWeeklyForecast('rice', 3);
console.log(`Trend: ${forecast.overall_statistics.overall_trend}`);
console.log(`Total Weeks: ${forecast.total_weeks}`);

forecast.weekly_forecasts.forEach(week => {
  console.log(`Week ${week.week_number}: ₱${week.average_forecast}`);
});
```

### Python
```python
import requests

# Get weekly forecast
response = requests.get('http://localhost:8000/forecast-weekly/rice/3')
data = response.json()

print(f"Commodity: {data['commodity']}")
print(f"Trend: {data['overall_statistics']['overall_trend']}")

for week in data['weekly_forecasts']:
    print(f"Week {week['week_number']}: ₱{week['average_forecast']}")
```

### React Example
```jsx
import React, { useEffect, useState } from 'react';

function ForecastDashboard() {
  const [forecast, setForecast] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/forecast-weekly/rice/3')
      .then(res => res.json())
      .then(data => setForecast(data));
  }, []);
  
  if (!forecast) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Rice Price Forecast - 3 Months</h1>
      <p>Trend: {forecast.overall_statistics.overall_trend}</p>
      <p>Price Change: ₱{forecast.overall_statistics.price_change}</p>
      
      <div>
        {forecast.weekly_forecasts.map(week => (
          <div key={week.week_number}>
            <h3>{week.week_label}</h3>
            <p>Average: ₱{week.average_forecast}</p>
            <p>{week.date_range}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### React Native Example
```jsx
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

function ForecastScreen() {
  const [forecast, setForecast] = useState(null);
  
  useEffect(() => {
    // Replace with your deployed URL or local IP
    fetch('http://192.168.1.100:8000/forecast-weekly/rice/3')
      .then(res => res.json())
      .then(data => setForecast(data))
      .catch(err => console.error(err));
  }, []);
  
  if (!forecast) return <Text>Loading...</Text>;
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Rice Price Forecast</Text>
      <Text>Trend: {forecast.overall_statistics.overall_trend}</Text>
      <Text>Change: ₱{forecast.overall_statistics.price_change}</Text>
      
      <FlatList
        data={forecast.weekly_forecasts}
        keyExtractor={item => item.week_number.toString()}
        renderItem={({item}) => (
          <View style={styles.weekCard}>
            <Text style={styles.weekTitle}>{item.week_label}</Text>
            <Text style={styles.price}>₱{item.average_forecast}</Text>
            <Text style={styles.dateRange}>{item.date_range}</Text>
            <Text>Range: ₱{item.min_forecast} - ₱{item.max_forecast}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
  weekCard: { padding: 15, marginVertical: 5, backgroundColor: '#f0f0f0', borderRadius: 8 },
  weekTitle: { fontSize: 18, fontWeight: '600' },
  price: { fontSize: 22, fontWeight: 'bold', color: '#2e7d32', marginVertical: 5 },
  dateRange: { fontSize: 12, color: '#666' }
});
```

## 🚀 Deployment to Render

### Option 1: Using Web Interface

1. **Prepare your code**
   - Push your code to GitHub
   - Make sure `requirements.txt` is in the root directory
   - Ensure `main.py` is in the root directory

2. **Create a new Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service**
   - **Name**: `price-forecast-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add environment variable (if needed)**
   - If you want to set a specific Python version: `PYTHON_VERSION=3.10.0`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your API will be live at: `https://price-forecast-api.onrender.com`

### Option 2: Using render.yaml (Automated)

See `render.yaml` file in this repository for automated deployment configuration.

## 📝 Data Format

The API expects an Excel file named `All Pricing Daily.xlsx` with the following columns:
- **Commodity**: Name of the commodity
- **Type**: Type/variant of the commodity
- **Specification**: Additional specifications
- **Amount**: Price value
- **Date**: Date of the price record

## 🔧 Configuration

### CORS Settings
By default, CORS is enabled for all origins. To restrict to specific domains, modify `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Configuration
Default port is 8000. Change it in the run command:
```bash
uvicorn main:app --reload --port 3000
```

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Install missing dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Prophet optimization failed"
**Solution**: This is expected. The API automatically falls back to a simple linear model which works well for most cases.

### Issue: "Port already in use"
**Solution**: Use a different port or kill the existing process
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: Cannot connect from mobile device
**Solution**: 
1. Make sure your device is on the same network
2. Use your computer's IP address instead of localhost
3. Check firewall settings

## 📊 Forecasting Methods

The API uses two forecasting methods:

1. **Prophet**: Facebook's forecasting library (primary method)
   - Advanced time series forecasting
   - Handles seasonality and trends
   - Falls back to simple method if optimization fails

2. **Enhanced Linear Model** (fallback):
   - Linear trend analysis
   - Seasonal adjustments for longer periods
   - Dynamic uncertainty bounds
   - Outlier removal

## 📈 Best Practices

1. **For real-time applications**: Use daily forecasts (7-30 days)
2. **For planning**: Use weekly forecasts (3-6 months)
3. **For long-term strategy**: Use extended forecasts (12-24 months)
4. **Cache responses**: Cache API responses to reduce load
5. **Error handling**: Always implement proper error handling in your application

## 📄 License

This project is open source and available for use.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the interactive docs at `/docs`
3. Test endpoints using the examples provided

## 🔄 Updates

To update the API with new data:
1. Replace `All Pricing Daily.xlsx` with updated file
2. Restart the server
3. API will automatically load new data

---

**Built with FastAPI, Prophet, and Pandas**

🌟 **Quick Start**: `uvicorn main:app --reload` → http://localhost:8000/docs

