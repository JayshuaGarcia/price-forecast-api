#!/usr/bin/env python3
"""
Keep Render API awake by pinging it every 10 minutes
Run this script on your computer or a free service
"""

import requests
import time
import schedule
from datetime import datetime

# Your deployed API URL (replace with your actual Render URL)
API_URL = "https://price-forecast-api.onrender.com"  # Update this after deployment

def ping_api():
    """Ping the API to keep it awake"""
    try:
        response = requests.get(f"{API_URL}/", timeout=30)
        if response.status_code == 200:
            print(f"✅ {datetime.now().strftime('%H:%M:%S')} - API is awake!")
        else:
            print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} - API responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ {datetime.now().strftime('%H:%M:%S')} - Failed to ping API: {e}")

def main():
    print("🔄 Starting API keep-alive service...")
    print(f"🌐 Monitoring: {API_URL}")
    print("⏰ Pinging every 10 minutes...")
    
    # Schedule ping every 10 minutes
    schedule.every(10).minutes.do(ping_api)
    
    # Initial ping
    ping_api()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
