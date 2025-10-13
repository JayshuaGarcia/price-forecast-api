#!/usr/bin/env python3
"""
UptimeRobot Setup Helper
This script helps you set up monitoring for your Render API
"""

import webbrowser
import time

def setup_uptimerobot():
    print("🤖 UptimeRobot Setup Helper")
    print("=" * 40)
    
    # Get Render URL from user
    render_url = input("Enter your Render API URL (e.g., https://price-forecast-api.onrender.com): ").strip()
    
    if not render_url.startswith('http'):
        render_url = f"https://{render_url}"
    
    print(f"\n✅ Your API URL: {render_url}")
    
    # Open UptimeRobot signup
    print("\n🌐 Opening UptimeRobot...")
    webbrowser.open("https://uptimerobot.com")
    
    print("\n📋 Setup Instructions:")
    print("1. Sign up for free account at UptimeRobot")
    print("2. Click 'Add New Monitor'")
    print("3. Use these settings:")
    print(f"   - Monitor Type: HTTP(s)")
    print(f"   - Friendly Name: Price Forecast API")
    print(f"   - URL: {render_url}")
    print(f"   - Interval: 5 minutes")
    print(f"   - Timeout: 30 seconds")
    print("4. Click 'Create Monitor'")
    print("\n🎉 Your API will stay awake 24/7!")
    
    # Test the API
    print(f"\n🧪 Testing your API...")
    try:
        import requests
        response = requests.get(render_url, timeout=10)
        if response.status_code == 200:
            print("✅ API is working!")
        else:
            print(f"⚠️ API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Could not reach API: {e}")
        print("Make sure your Render deployment is complete.")

if __name__ == "__main__":
    setup_uptimerobot()
