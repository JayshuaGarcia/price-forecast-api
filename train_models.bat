@echo off
echo TRAINING ALL COMMODITY MODELS - ONE-TIME OFFLINE TRAINING
echo =========================================================

echo.
echo Training Rice model...
curl -X POST http://localhost:8000/train/rice

echo.
echo Training Corn model...
curl -X POST http://localhost:8000/train/corn

echo.
echo Training Fish model...
curl -X POST http://localhost:8000/train/fish

echo.
echo Training all commodities at once...
curl -X POST http://localhost:8000/train-all

echo.
echo TRAINING COMPLETE!
echo Models are now cached for faster predictions.
pause

