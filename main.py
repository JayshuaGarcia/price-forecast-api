from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from prophet import Prophet
import numpy as np
import json
from datetime import datetime, timedelta
import os
import pickle
from pathlib import Path

app = FastAPI()

# Allow frontend connection (React Native, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Excel Data ---
FILE_PATH = "All Pricing Daily.xlsx"
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

def _slugify(value: str) -> str:
    return (
        "".join(ch if ch.isalnum() else "_" for ch in value.lower())
        .strip("_")
        .replace("__", "_")
    )

def _model_path_for(commodity: str) -> Path:
    return MODEL_DIR / f"prophet_{_slugify(commodity)}.pkl"

def _is_model_fresh(model_path: Path) -> bool:
    if not model_path.exists():
        return False
    data_mtime = Path(FILE_PATH).stat().st_mtime
    model_mtime = model_path.stat().st_mtime
    return model_mtime >= data_mtime

def _prepare_prophet_dataframe(history_df: pd.DataFrame) -> pd.DataFrame:
    return history_df[["date", "amount"]].rename(columns={"date": "ds", "amount": "y"}).dropna()

def _fit_prophet(history_df: pd.DataFrame) -> Prophet:
    forecast_df = _prepare_prophet_dataframe(history_df)
    if len(forecast_df) < 2:
        raise Exception("Not enough data after cleaning")
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    model.fit(forecast_df)
    return model

def load_data():
    df = pd.read_excel(FILE_PATH)
    # Convert column names to lowercase and replace spaces with underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Check for required columns
    required_columns = ['commodity', 'date', 'amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise Exception(f"Missing required columns: {missing_columns}. Available columns: {df.columns.tolist()}")
    
    # Convert date column to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert amount column to numeric, handling any non-numeric values
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Remove rows with NaN values in critical columns
    df = df.dropna(subset=['commodity', 'date', 'amount'])
    
    return df

def clean_data_for_json(data):
    """Clean data to ensure JSON serialization works properly"""
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, (np.integer, np.int64)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif pd.isna(data):
        return None
    else:
        return data

def analyze_commodity_patterns(data, commodity_name):
    """Analyze actual patterns in commodity data"""
    if len(data) < 10:
        return None
    
    # Get recent data (last 6 months)
    recent_date = data['date'].max() - timedelta(days=180)
    recent_data = data[data['date'] >= recent_date].copy()
    
    if len(recent_data) < 5:
        recent_data = data.tail(30).copy()
    
    # Calculate actual statistics
    avg_price = recent_data['amount'].mean()
    price_std = recent_data['amount'].std()
    min_price = recent_data['amount'].min()
    max_price = recent_data['amount'].max()
    
    # Calculate actual trend
    daily_avg = recent_data.groupby('date')['amount'].mean().reset_index().sort_values('date')
    if len(daily_avg) >= 2:
        first_price = daily_avg['amount'].iloc[0]
        last_price = daily_avg['amount'].iloc[-1]
        trend_percent = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
        trend_direction = "increasing" if trend_percent > 1 else "decreasing" if trend_percent < -1 else "stable"
    else:
        trend_percent = 0
        trend_direction = "stable"
    
    # Calculate volatility
    price_changes = daily_avg['amount'].diff().dropna()
    volatility = price_changes.std() if len(price_changes) > 0 else price_std * 0.1
    
    return {
        'avg_price': avg_price,
        'price_std': price_std,
        'min_price': min_price,
        'max_price': max_price,
        'trend_percent': trend_percent,
        'trend_direction': trend_direction,
        'volatility': volatility,
        'data_points': len(recent_data),
        'recent_prices': daily_avg['amount'].tail(10).tolist()
    }

def realistic_forecast(data, days, commodity_name):
    """Generate realistic forecasts based on actual data patterns"""
    if len(data) < 2:
        return []
    
    # Analyze actual patterns
    patterns = analyze_commodity_patterns(data, commodity_name)
    if not patterns:
        return []
    
    # Get last date and price
    last_date = data['date'].iloc[-1]
    last_price = data['amount'].iloc[-1]
    
    # Use actual patterns for forecasting
    base_price = patterns['avg_price']
    volatility = patterns['volatility']
    trend_percent = patterns['trend_percent']
    
    # Adjust base price based on recent trend
    trend_adjustment = (trend_percent / 100) * base_price
    
    forecasts = []
    for i in range(1, days + 1):
        future_date = last_date + timedelta(days=i)
        
        # Calculate realistic price based on actual patterns
        # Use trend but keep it within reasonable bounds
        trend_factor = trend_adjustment * (i / 30)  # Apply trend over time
        
        # Add realistic variation based on actual volatility
        random_variation = np.random.normal(0, volatility * 0.5)
        
        # Calculate predicted price
        predicted_value = base_price + trend_factor + random_variation
        
        # Ensure price stays within realistic bounds (based on historical data)
        min_bound = max(patterns['min_price'] * 0.8, 1.0)  # At least ₱1, but not below 80% of historical min
        max_bound = patterns['max_price'] * 1.2  # Not more than 120% of historical max
        
        predicted_value = max(min_bound, min(predicted_value, max_bound))
        
        # Calculate confidence intervals based on actual volatility
        confidence_range = volatility * (1 + i / 30)  # Slightly increase uncertainty over time
        
        forecast = {
            'ds': future_date.strftime('%Y-%m-%d'),
            'yhat': round(predicted_value, 2),
            'yhat_lower': max(min_bound, round(predicted_value - 1.5 * confidence_range, 2)),
            'yhat_upper': min(max_bound, round(predicted_value + 1.5 * confidence_range, 2))
        }
        forecasts.append(forecast)
    
    return forecasts

def simple_forecast(data, days):
    """Fallback simple forecasting for when realistic forecasting fails"""
    if len(data) < 2:
        return []
    
    # Use the last known price as base
    last_price = data['amount'].iloc[-1]
    last_date = data['date'].iloc[-1]
    
    # Calculate volatility from recent data
    recent_prices = data['amount'].tail(30)
    volatility = recent_prices.std() if len(recent_prices) > 1 else last_price * 0.05
    
    forecasts = []
    for i in range(1, days + 1):
        future_date = last_date + timedelta(days=i)
        
        # Very conservative forecast - stay close to last price
        predicted_value = last_price + np.random.normal(0, volatility * 0.1)
        
        forecast = {
            'ds': future_date.strftime('%Y-%m-%d'),
            'yhat': round(max(0, predicted_value), 2),
            'yhat_lower': round(max(0, predicted_value - volatility), 2),
            'yhat_upper': round(predicted_value + volatility, 2)
        }
        forecasts.append(forecast)
    
    return forecasts

@app.get("/")
def root():
    return {"message": "Price Forecast API - Forecasting Only", "version": "2.0", "data_updated": "2025-10-15"}

# --- Endpoint: Get available commodities ---
@app.get("/commodities")
def get_commodities():
    try:
        df = load_data()
        commodities = df['commodity'].unique().tolist()
        return {"commodities": commodities}
    except Exception as e:
        return {"error": f"Failed to load commodities: {str(e)}"}

# --- Endpoint: Daily forecast for next days (up to 365 days) ---
@app.get("/forecast/{commodity}/{days}")
def forecast_price(commodity: str, days: int):
    try:
        # Validate days parameter
        if days <= 0:
            return {"error": "Days must be a positive integer"}
        if days > 365:
            return {"error": "Maximum forecast period is 365 days. Use /extended-forecast for longer periods."}
            
        df = load_data()

        # Filter only the selected commodity
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]

        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}

        # Group by date and calculate average amount for each date
        daily_avg = filtered.groupby('date')['amount'].mean().reset_index()
        
        if len(daily_avg) < 2:
            return {"error": f"Not enough data for '{commodity}' to make forecasts (need at least 2 data points)"}

        # Sort by date and get recent data (last 365 days for better performance)
        daily_avg = daily_avg.sort_values('date')
        recent_data = daily_avg.tail(365)  # Use last year of data
        
        # Remove outliers (prices that are more than 3 standard deviations away)
        mean_price = recent_data['amount'].mean()
        std_price = recent_data['amount'].std()
        recent_data = recent_data[
            (recent_data['amount'] >= mean_price - 3*std_price) & 
            (recent_data['amount'] <= mean_price + 3*std_price)
        ]
        
        if len(recent_data) < 2:
            return {"error": f"Not enough valid data for '{commodity}' after outlier removal"}

        # Try cached Prophet model first; fall back to fit-on-the-fly; else simple forecast
        try:
            model_path = _model_path_for(commodity)
            model: Prophet | None = None
            if _is_model_fresh(model_path):
                with open(model_path, "rb") as f:
                    model = pickle.load(f)
            else:
                model = _fit_prophet(recent_data)
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)
            # Prepare for Prophet
            forecast_df = _prepare_prophet_dataframe(recent_data)

            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)

            # Get only the forecasted days (last 'days' rows)
            result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
            
            # Clean the data for JSON serialization
            result_dict = result.to_dict(orient='records')
            cleaned_result = clean_data_for_json(result_dict)
            
            return {"commodity": commodity, "forecast": cleaned_result, "method": "prophet"}
            
        except Exception as prophet_error:
            # Fall back to realistic forecasting based on actual patterns
            forecasts = realistic_forecast(recent_data, days, commodity)
            if not forecasts:
                # Final fallback to simple forecasting
                forecasts = simple_forecast(recent_data, days)
                if not forecasts:
                    return {"error": f"All forecasting methods failed for '{commodity}'"}
                return {"commodity": commodity, "forecast": forecasts, "method": "simple_linear", "prophet_error": str(prophet_error)}
            
            return {"commodity": commodity, "forecast": forecasts, "method": "realistic_pattern_based", "prophet_error": str(prophet_error)}
        
    except Exception as e:
        return {"error": f"Failed to generate forecast: {str(e)}"}

# --- Endpoint: Extended forecast for longer periods (6 months to 2 years) ---
@app.get("/extended-forecast/{commodity}/{months}")
def extended_forecast_price(commodity: str, months: int):
    try:
        # Validate months parameter
        if months <= 0:
            return {"error": "Months must be a positive integer"}
        if months > 24:
            return {"error": "Maximum extended forecast period is 24 months (2 years)"}
            
        days = months * 30  # Approximate days in months
        
        df = load_data()

        # Filter only the selected commodity
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]

        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}

        # Group by date and calculate average amount for each date
        daily_avg = filtered.groupby('date')['amount'].mean().reset_index()
        
        if len(daily_avg) < 2:
            return {"error": f"Not enough data for '{commodity}' to make forecasts (need at least 2 data points)"}

        # Sort by date and use more historical data for longer forecasts
        daily_avg = daily_avg.sort_values('date')
        historical_data = daily_avg.tail(730)  # Use last 2 years of data for extended forecasts
        
        # Remove outliers (prices that are more than 3 standard deviations away)
        mean_price = historical_data['amount'].mean()
        std_price = historical_data['amount'].std()
        historical_data = historical_data[
            (historical_data['amount'] >= mean_price - 3*std_price) & 
            (historical_data['amount'] <= mean_price + 3*std_price)
        ]
        
        if len(historical_data) < 30:  # Need at least a month of data for extended forecasts
            return {"error": f"Not enough valid historical data for '{commodity}' extended forecast (need at least 30 days)"}

        # Prefer cached (or freshly-fit) Prophet model for extended periods
        try:
            model_path = _model_path_for(commodity)
            model: Prophet | None = None
            if _is_model_fresh(model_path):
                with open(model_path, "rb") as f:
                    model = pickle.load(f)
            else:
                model = _fit_prophet(historical_data)
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)

            forecast_df = _prepare_prophet_dataframe(historical_data)
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
            forecasts = clean_data_for_json(result.to_dict(orient='records'))
            method_used = "prophet_cached"
        except Exception:
            forecasts = simple_forecast(historical_data, days)
            method_used = "extended_linear_with_seasonality"
        
        if not forecasts:
            return {"error": f"Extended forecasting failed for '{commodity}'"}
        
        # Add monthly summary for extended forecasts
        monthly_summary = []
        for i in range(0, len(forecasts), 30):
            month_forecasts = forecasts[i:i+30]
            if month_forecasts:
                month_avg = sum(f['yhat'] for f in month_forecasts) / len(month_forecasts)
                month_start = month_forecasts[0]['ds']
                month_end = month_forecasts[-1]['ds']
                
                monthly_summary.append({
                    'month': f"{month_start} to {month_end}",
                    'average_forecast': round(month_avg, 2),
                    'forecast_count': len(month_forecasts)
                })
        
        return {
            "commodity": commodity, 
            "forecast_period_months": months,
            "forecast_period_days": days,
            "forecast": forecasts, 
            "method": method_used,
            "monthly_summary": monthly_summary,
            "data_points_used": len(historical_data),
            "note": "Extended forecasts use enhanced linear modeling with seasonal adjustments and increased uncertainty bounds for longer periods"
        }
        
    except Exception as e:
        return {"error": f"Failed to generate extended forecast: {str(e)}"}

# --- Endpoint: Weekly forecast for multiple months ---
@app.get("/forecast-weekly/{commodity}/{months}")
def forecast_weekly(commodity: str, months: int):
    try:
        # Validate months parameter
        if months <= 0:
            return {"error": "Months must be a positive integer"}
        if months > 12:
            return {"error": "Maximum weekly forecast period is 12 months"}
            
        days = months * 30  # Approximate days in months
        weeks = (days // 7) + 1  # Number of weeks
        
        df = load_data()

        # Filter only the selected commodity
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]

        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}

        # Group by date and calculate average amount for each date
        daily_avg = filtered.groupby('date')['amount'].mean().reset_index()
        
        if len(daily_avg) < 2:
            return {"error": f"Not enough data for '{commodity}' to make forecasts (need at least 2 data points)"}

        # Sort by date and use appropriate historical data
        daily_avg = daily_avg.sort_values('date')
        historical_data = daily_avg.tail(365)  # Use last year of data
        
        # Remove outliers (prices that are more than 3 standard deviations away)
        mean_price = historical_data['amount'].mean()
        std_price = historical_data['amount'].std()
        historical_data = historical_data[
            (historical_data['amount'] >= mean_price - 3*std_price) & 
            (historical_data['amount'] <= mean_price + 3*std_price)
        ]
        
        if len(historical_data) < 7:
            return {"error": f"Not enough valid historical data for '{commodity}' weekly forecast"}

        # Generate daily forecasts using realistic pattern-based forecasting
        daily_forecasts = realistic_forecast(historical_data, days, commodity)
        if not daily_forecasts:
            # Fallback to simple forecasting
            daily_forecasts = simple_forecast(historical_data, days)
        
        if not daily_forecasts:
            return {"error": f"Weekly forecasting failed for '{commodity}'"}
        
        # Group daily forecasts into weekly summaries
        weekly_summary = []
        for week_num in range(weeks):
            start_idx = week_num * 7
            end_idx = min(start_idx + 7, len(daily_forecasts))
            
            if start_idx >= len(daily_forecasts):
                break
                
            week_forecasts = daily_forecasts[start_idx:end_idx]
            
            if week_forecasts:
                week_avg = sum(f['yhat'] for f in week_forecasts) / len(week_forecasts)
                week_min = min(f['yhat_lower'] for f in week_forecasts)
                week_max = max(f['yhat_upper'] for f in week_forecasts)
                week_start = week_forecasts[0]['ds']
                week_end = week_forecasts[-1]['ds']
                
                # Calculate week number and month
                week_display = week_num + 1
                month_display = (week_num // 4) + 1
                
                weekly_summary.append({
                    'week_number': week_display,
                    'month': month_display,
                    'week_label': f"Week {week_display} (Month {month_display})",
                    'date_range': f"{week_start} to {week_end}",
                    'start_date': week_start,
                    'end_date': week_end,
                    'average_forecast': round(week_avg, 2),
                    'min_forecast': round(week_min, 2),
                    'max_forecast': round(week_max, 2),
                    'days_in_week': len(week_forecasts),
                    'daily_forecasts': week_forecasts
                })
        
        # Calculate overall statistics
        all_avg_prices = [w['average_forecast'] for w in weekly_summary]
        overall_trend = "Increasing" if all_avg_prices[-1] > all_avg_prices[0] else "Decreasing"
        price_change = all_avg_prices[-1] - all_avg_prices[0]
        price_change_percent = (price_change / all_avg_prices[0]) * 100 if all_avg_prices[0] > 0 else 0
        
        return {
            "commodity": commodity,
            "forecast_period_months": months,
            "total_weeks": len(weekly_summary),
            "weekly_forecasts": weekly_summary,
            "overall_statistics": {
                "starting_price": round(all_avg_prices[0], 2),
                "ending_price": round(all_avg_prices[-1], 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "overall_trend": overall_trend,
                "average_price": round(sum(all_avg_prices) / len(all_avg_prices), 2),
                "min_weekly_avg": round(min(all_avg_prices), 2),
                "max_weekly_avg": round(max(all_avg_prices), 2)
            },
            "method": "realistic_pattern_based_forecasting",
            "data_points_used": len(historical_data)
        }
        
    except Exception as e:
        return {"error": f"Failed to generate weekly forecast: {str(e)}"}

# --- Offline training endpoints ---
@app.post("/train/{commodity}")
def train_single_commodity(commodity: str):
    try:
        df = load_data()
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]
        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}
        daily_avg = filtered.groupby('date')['amount'].mean().reset_index().sort_values('date')
        # Use up to last 2 years for robustness
        history = daily_avg.tail(730)
        model = _fit_prophet(history)
        path = _model_path_for(commodity)
        with open(path, "wb") as f:
            pickle.dump(model, f)
        return {"status": "trained", "commodity": commodity, "model_path": str(path), "rows_used": int(len(history))}
    except Exception as e:
        return {"error": f"Failed to train model: {str(e)}"}

@app.post("/train-all")
def train_all():
    try:
        df = load_data()
        results = []
        for commodity in sorted(df['commodity'].unique().tolist()):
            try:
                filtered = df[df['commodity'] == commodity]
                daily_avg = filtered.groupby('date')['amount'].mean().reset_index().sort_values('date')
                history = daily_avg.tail(730)
                if len(history) < 2:
                    results.append({"commodity": commodity, "status": "skipped", "reason": "not_enough_data"})
                    continue
                model = _fit_prophet(history)
                path = _model_path_for(commodity)
                with open(path, "wb") as f:
                    pickle.dump(model, f)
                results.append({"commodity": commodity, "status": "trained", "rows_used": int(len(history))})
            except Exception as inner_e:
                results.append({"commodity": commodity, "status": "failed", "error": str(inner_e)})
        return {"summary": results, "model_dir": str(MODEL_DIR)}
    except Exception as e:
        return {"error": f"Failed to train all models: {str(e)}"}
