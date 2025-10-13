@echo off
cd /d "C:\Users\Mischelle\price-forecast-api"
uvicorn main:app --host 0.0.0.0 --port 8000
pause
