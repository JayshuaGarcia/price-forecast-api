# 🌾 Complete Products List for React Native Integration

## All Available Commodities in Your API

Your price forecast API provides weekly forecasts for these **11 commodities**:

### 📊 Product Categories:

1. **GRAINS & CEREALS**
   - `IMPORTED COMMERCIAL RICE`
   - `KADIWA RICE-FOR-ALL`
   - `LOCAL COMMERCIAL RICE`

2. **PROTEIN SOURCES**
   - `FISH (per kg)`
   - `LIVESTOCK AND POULTRY PRODUCTS`

3. **FRUITS & VEGETABLES**
   - `FRUITS (per kg)`
   - `HIGHLAND VEGETABLES (per kg)`
   - `LOWLAND VEGETABLES (per kg)`

4. **STAPLE CROPS**
   - `CORN (per kg)`

5. **SEASONINGS & OTHERS**
   - `SPICES (per kg)`
   - `OTHER COMMODITIES`

## 🔗 API Endpoints for Each Product

### Base URL: `https://price-forecast-api.onrender.com`

### Weekly Forecasts (3 months):
```
/forecast-weekly/rice/3
/forecast-weekly/corn/3
/forecast-weekly/fish/3
/forecast-weekly/fruits/3
/forecast-weekly/highland%20vegetables/3
/forecast-weekly/lowland%20vegetables/3
/forecast-weekly/spices/3
/forecast-weekly/other%20commodities/3
/forecast-weekly/livestock%20and%20poultry%20products/3
/forecast-weekly/imported%20commercial%20rice/3
/forecast-weekly/kadiwa%20rice-for-all/3
/forecast-weekly/local%20commercial%20rice/3
```

### Daily Forecasts (7 days):
```
/forecast/rice/7
/forecast/corn/7
/forecast/fish/7
/forecast/fruits/7
/forecast/highland%20vegetables/7
/forecast/lowland%20vegetables/7
/forecast/spices/7
/forecast/other%20commodities/7
/forecast/livestock%20and%20poultry%20products/7
/forecast/imported%20commercial%20rice/7
/forecast/kadiwa%20rice-for-all/7
/forecast/local%20commercial%20rice/7
```

## 📱 React Native Implementation

```javascript
const API_BASE_URL = 'https://price-forecast-api.onrender.com';

// All commodities
const commodities = [
  'rice',
  'corn', 
  'fish',
  'fruits',
  'highland vegetables',
  'lowland vegetables',
  'spices',
  'other commodities',
  'livestock and poultry products',
  'imported commercial rice',
  'kadiwa rice-for-all',
  'local commercial rice'
];

// Get weekly forecast for any commodity
const getWeeklyForecast = async (commodity, months = 3) => {
  try {
    const response = await fetch(`${API_BASE_URL}/forecast-weekly/${encodeURIComponent(commodity)}/${months}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching forecast:', error);
    throw error;
  }
};

// Get daily forecast for any commodity
const getDailyForecast = async (commodity, days = 7) => {
  try {
    const response = await fetch(`${API_BASE_URL}/forecast/${encodeURIComponent(commodity)}/${days}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching forecast:', error);
    throw error;
  }
};

// Usage examples:
// const riceWeekly = await getWeeklyForecast('rice', 3);
// const cornDaily = await getDailyForecast('corn', 7);
// const fishWeekly = await getWeeklyForecast('fish', 6);
```

## 🎯 Response Format

Each weekly forecast returns:
```json
{
  "commodity": "rice",
  "forecast_period_months": 3,
  "total_weeks": 13,
  "weekly_forecasts": [
    {
      "week_number": 1,
      "week_label": "Week 1 (Month 1)",
      "date_range": "2025-10-01 to 2025-10-07",
      "average_forecast": 51.71,
      "min_forecast": 51.62,
      "max_forecast": 51.79,
      "weekly_trend": "Stable"
    }
  ],
  "overall_statistics": {
    "starting_price": 51.71,
    "ending_price": 52.15,
    "price_change": 0.44,
    "price_change_percent": 0.85,
    "overall_trend": "Up"
  }
}
```

## 🚀 Ready to Use!

Your React Native app can now:
- ✅ **Load all 11 commodities** automatically
- ✅ **Get weekly forecasts** for any product
- ✅ **Get daily forecasts** for any product
- ✅ **Display price trends** and changes
- ✅ **Handle all product types** from your Excel data

**Perfect for agricultural price monitoring, commodity trading, and market analysis apps!**

