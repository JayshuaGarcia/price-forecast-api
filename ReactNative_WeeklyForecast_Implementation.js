// ========================================
// REACT NATIVE WEEKLY PRICE FORECAST IMPLEMENTATION
// ========================================

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';

// ========================================
// 1. API CONFIGURATION
// ========================================
const API_BASE_URL = 'https://price-forecast-api.onrender.com'; // Your deployed API
// For local testing: 'http://localhost:8000'

// ========================================
// 2. API SERVICE FUNCTIONS
// ========================================
class PriceForecastAPI {
  static async getCommodities() {
    try {
      const response = await fetch(`${API_BASE_URL}/commodities`);
      if (!response.ok) throw new Error('Failed to fetch commodities');
      return await response.json();
    } catch (error) {
      console.error('Error fetching commodities:', error);
      throw error;
    }
  }

  static async getWeeklyForecast(commodity, months = 3) {
    try {
      const response = await fetch(`${API_BASE_URL}/forecast-weekly/${commodity}/${months}`);
      if (!response.ok) throw new Error(`Failed to fetch forecast for ${commodity}`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching weekly forecast for ${commodity}:`, error);
      throw error;
    }
  }

  static async getDailyForecast(commodity, days = 7) {
    try {
      const response = await fetch(`${API_BASE_URL}/forecast/${commodity}/${days}`);
      if (!response.ok) throw new Error(`Failed to fetch daily forecast for ${commodity}`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching daily forecast for ${commodity}:`, error);
      throw error;
    }
  }
}

// ========================================
// 3. COMPONENTS
// ========================================

// Weekly Forecast Card Component
const WeeklyForecastCard = ({ forecast, onPress }) => (
  <TouchableOpacity style={styles.forecastCard} onPress={onPress}>
    <View style={styles.cardHeader}>
      <Text style={styles.commodityName}>{forecast.commodity}</Text>
      <Text style={styles.forecastPeriod}>{forecast.forecast_period_months} months</Text>
    </View>
    
    <View style={styles.statsContainer}>
      <View style={styles.statItem}>
        <Text style={styles.statLabel}>Starting Price</Text>
        <Text style={styles.statValue}>₱{forecast.overall_statistics.starting_price}</Text>
      </View>
      
      <View style={styles.statItem}>
        <Text style={styles.statLabel}>Ending Price</Text>
        <Text style={styles.statValue}>₱{forecast.overall_statistics.ending_price}</Text>
      </View>
      
      <View style={styles.statItem}>
        <Text style={styles.statLabel}>Change</Text>
        <Text style={[
          styles.statValue,
          { color: forecast.overall_statistics.price_change >= 0 ? '#4CAF50' : '#F44336' }
        ]}>
          {forecast.overall_statistics.price_change >= 0 ? '+' : ''}₱{forecast.overall_statistics.price_change.toFixed(2)}
        </Text>
      </View>
      
      <View style={styles.statItem}>
        <Text style={styles.statLabel}>Trend</Text>
        <Text style={[
          styles.statValue,
          { color: forecast.overall_statistics.overall_trend === 'Up' ? '#4CAF50' : '#F44336' }
        ]}>
          {forecast.overall_statistics.overall_trend}
        </Text>
      </View>
    </View>
    
    <Text style={styles.weeksCount}>{forecast.total_weeks} weeks forecast</Text>
  </TouchableOpacity>
);

// Weekly Detail View Component
const WeeklyDetailView = ({ forecast, onClose }) => (
  <View style={styles.detailContainer}>
    <View style={styles.detailHeader}>
      <Text style={styles.detailTitle}>{forecast.commodity} - Weekly Forecast</Text>
      <TouchableOpacity onPress={onClose} style={styles.closeButton}>
        <Text style={styles.closeButtonText}>✕</Text>
      </TouchableOpacity>
    </View>
    
    <ScrollView style={styles.weeklyList}>
      {forecast.weekly_forecasts.map((week, index) => (
        <View key={index} style={styles.weekItem}>
          <View style={styles.weekHeader}>
            <Text style={styles.weekLabel}>{week.week_label}</Text>
            <Text style={styles.weekRange}>{week.date_range}</Text>
          </View>
          
          <View style={styles.weekStats}>
            <View style={styles.priceContainer}>
              <Text style={styles.priceLabel}>Average</Text>
              <Text style={styles.priceValue}>₱{week.average_forecast.toFixed(2)}</Text>
            </View>
            
            <View style={styles.priceContainer}>
              <Text style={styles.priceLabel}>Range</Text>
              <Text style={styles.priceRange}>
                ₱{week.min_forecast.toFixed(2)} - ₱{week.max_forecast.toFixed(2)}
              </Text>
            </View>
          </View>
        </View>
      ))}
    </ScrollView>
  </View>
);

// ========================================
// 4. MAIN COMPONENT
// ========================================
const WeeklyPriceForecastApp = () => {
  const [commodities, setCommodities] = useState([]);
  const [forecasts, setForecasts] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedForecast, setSelectedForecast] = useState(null);
  const [error, setError] = useState(null);

  // Load all commodities and their weekly forecasts
  useEffect(() => {
    loadAllForecasts();
  }, []);

  const loadAllForecasts = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get all commodities
      const commoditiesData = await PriceForecastAPI.getCommodities();
      setCommodities(commoditiesData.commodities);

      // Load weekly forecasts for all commodities (3 months each)
      const forecastPromises = commoditiesData.commodities.map(async (commodity) => {
        try {
          const forecast = await PriceForecastAPI.getWeeklyForecast(commodity, 3);
          return { commodity, forecast };
        } catch (error) {
          console.error(`Failed to load forecast for ${commodity}:`, error);
          return { commodity, forecast: null, error: error.message };
        }
      });

      const results = await Promise.all(forecastPromises);
      const forecastMap = {};
      
      results.forEach(({ commodity, forecast, error }) => {
        if (forecast) {
          forecastMap[commodity] = forecast;
        } else {
          forecastMap[commodity] = { error };
        }
      });

      setForecasts(forecastMap);
    } catch (error) {
      setError('Failed to load data. Please check your internet connection.');
      console.error('Error loading forecasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleForecastPress = (commodity) => {
    const forecast = forecasts[commodity];
    if (forecast && !forecast.error) {
      setSelectedForecast(forecast);
    } else {
      Alert.alert('Error', `Failed to load forecast for ${commodity}`);
    }
  };

  const renderForecastItem = ({ item: commodity }) => {
    const forecast = forecasts[commodity];
    
    if (!forecast) {
      return (
        <View style={styles.loadingCard}>
          <ActivityIndicator size="small" color="#2196F3" />
          <Text style={styles.loadingText}>Loading {commodity}...</Text>
        </View>
      );
    }

    if (forecast.error) {
      return (
        <View style={styles.errorCard}>
          <Text style={styles.errorText}>{commodity}</Text>
          <Text style={styles.errorSubtext}>Failed to load</Text>
        </View>
      );
    }

    return (
      <WeeklyForecastCard
        forecast={forecast}
        onPress={() => handleForecastPress(commodity)}
      />
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>Loading price forecasts...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadAllForecasts}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (selectedForecast) {
    return (
      <WeeklyDetailView
        forecast={selectedForecast}
        onClose={() => setSelectedForecast(null)}
      />
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Weekly Price Forecasts</Text>
        <Text style={styles.headerSubtitle}>3-Month Forecasts for All Commodities</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={loadAllForecasts}>
          <Text style={styles.refreshButtonText}>🔄 Refresh</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={commodities}
        renderItem={renderForecastItem}
        keyExtractor={(item) => item}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

// ========================================
// 5. STYLES
// ========================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 10,
  },
  refreshButton: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  refreshButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  listContainer: {
    padding: 15,
  },
  forecastCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  commodityName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  forecastPeriod: {
    fontSize: 12,
    color: '#666',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  weeksCount: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  loadingCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  errorCard: {
    backgroundColor: '#ffebee',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#c62828',
  },
  errorSubtext: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  detailContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  detailHeader: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
  },
  closeButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    width: 30,
    height: 30,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  weeklyList: {
    flex: 1,
    padding: 15,
  },
  weekItem: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
  },
  weekHeader: {
    marginBottom: 10,
  },
  weekLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  weekRange: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  weekStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  priceContainer: {
    flex: 1,
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  priceRange: {
    fontSize: 14,
    color: '#666',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  retryButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    marginTop: 15,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});

export default WeeklyPriceForecastApp;

// ========================================
// 6. USAGE INSTRUCTIONS
// ========================================

/*
HOW TO USE THIS IN YOUR REACT NATIVE PROJECT:

1. COPY THIS FILE TO YOUR PROJECT:
   - Save as: WeeklyPriceForecast.js

2. INSTALL REQUIRED DEPENDENCIES:
   npm install react-native-vector-icons
   
   Or if using Expo:
   expo install @expo/vector-icons

3. IMPORT AND USE IN YOUR APP:
   import WeeklyPriceForecastApp from './WeeklyPriceForecast';
   
   // In your main App.js or screen component:
   export default function App() {
     return <WeeklyPriceForecastApp />;
   }

4. CUSTOMIZE THE API URL:
   - Change API_BASE_URL to your deployed Render URL
   - For testing: use 'http://localhost:8000'

5. FEATURES INCLUDED:
   ✅ Loads all 11 commodities automatically
   ✅ Shows 3-month weekly forecasts
   ✅ Displays price trends and changes
   ✅ Tap to see detailed weekly breakdown
   ✅ Error handling and loading states
   ✅ Refresh functionality
   ✅ Responsive design

6. CUSTOMIZATION OPTIONS:
   - Change forecast period (currently 3 months)
   - Modify colors and styling
   - Add more forecast types (daily, extended)
   - Add filtering and search
   - Add charts and graphs

7. API ENDPOINTS USED:
   - GET /commodities - Get all available commodities
   - GET /forecast-weekly/{commodity}/{months} - Get weekly forecast

EXAMPLE API RESPONSE STRUCTURE:
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
*/

