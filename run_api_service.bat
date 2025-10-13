@echo off
title Price Forecast API Server
echo Starting Price Forecast API...
echo.
echo Server will run at: http://localhost:8000
echo Interactive docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "C:\Users\Mischelle\price-forecast-api"
uvicorn main:app --host 0.0.0.0 --port 8000
