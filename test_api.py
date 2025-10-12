"""
Test script for the Price Forecast API
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_weekly_forecast():
    """Test the weekly forecast endpoint"""
    print("\n" + "="*60)
    print("🧪 TESTING WEEKLY FORECAST FOR RICE (3 MONTHS)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/forecast-weekly/rice/3")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ SUCCESS!")
        print(f"📦 Commodity: {data['commodity']}")
        print(f"📅 Forecast Period: {data['forecast_period_months']} months")
        print(f"📊 Total Weeks: {data['total_weeks']}")
        
        print("\n📈 OVERALL STATISTICS:")
        stats = data['overall_statistics']
        print(f"  Starting Price: ₱{stats['starting_price']}")
        print(f"  Ending Price: ₱{stats['ending_price']}")
        print(f"  Price Change: ₱{stats['price_change']} ({stats['price_change_percent']:.2f}%)")
        print(f"  Overall Trend: {stats['overall_trend']}")
        print(f"  Average Price: ₱{stats['average_price']}")
        print(f"  Min Weekly Avg: ₱{stats['min_weekly_avg']}")
        print(f"  Max Weekly Avg: ₱{stats['max_weekly_avg']}")
        
        print("\n📅 WEEKLY FORECASTS (First 5 weeks):")
        for week in data['weekly_forecasts'][:5]:
            print(f"\n  {week['week_label']}")
            print(f"    Date Range: {week['date_range']}")
            print(f"    Average: ₱{week['average_forecast']}")
            print(f"    Range: ₱{week['min_forecast']} - ₱{week['max_forecast']}")
        
        print(f"\n  ... and {len(data['weekly_forecasts']) - 5} more weeks")
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)

def test_commodities():
    """Test getting all commodities"""
    print("\n" + "="*60)
    print("🧪 TESTING GET COMMODITIES")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/commodities")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"📦 Total Commodities: {len(data['commodities'])}")
        print(f"📋 First 10 commodities:")
        for i, commodity in enumerate(data['commodities'][:10], 1):
            print(f"  {i}. {commodity}")
    else:
        print(f"❌ ERROR: {response.status_code}")

def test_daily_forecast():
    """Test daily forecast"""
    print("\n" + "="*60)
    print("🧪 TESTING DAILY FORECAST FOR RICE (7 DAYS)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/forecast/rice/7")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"📦 Commodity: {data['commodity']}")
        print(f"🔧 Method: {data['method']}")
        print(f"\n📅 DAILY FORECASTS:")
        for day in data['forecast']:
            print(f"  {day['ds']}: ₱{day['yhat']:.2f} (₱{day['yhat_lower']:.2f} - ₱{day['yhat_upper']:.2f})")
    else:
        print(f"❌ ERROR: {response.status_code}")

if __name__ == "__main__":
    print("\n🚀 PRICE FORECAST API TESTING")
    print("="*60)
    
    try:
        # Test 1: Get commodities
        test_commodities()
        
        # Test 2: Daily forecast
        test_daily_forecast()
        
        # Test 3: Weekly forecast
        test_weekly_forecast()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        print("\n💡 TIP: Try these endpoints:")
        print(f"  • Interactive Docs: {BASE_URL}/docs")
        print(f"  • Weekly Forecast: {BASE_URL}/forecast-weekly/rice/3")
        print(f"  • Daily Forecast: {BASE_URL}/forecast/rice/30")
        print(f"  • Commodities List: {BASE_URL}/commodities")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API")
        print("   Make sure the server is running:")
        print("   uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

