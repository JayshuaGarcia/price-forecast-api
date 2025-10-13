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

def simple_forecast(data, days):
    """Enhanced simple forecasting with seasonal adjustment for longer periods"""
    if len(data) < 2:
        return []
    
    # Calculate simple linear trend
    x = np.arange(len(data))
    y = data['amount'].values
    
    # Linear regression
    coeffs = np.polyfit(x, y, 1)
    trend = coeffs[0]
    
    # Calculate volatility and seasonal patterns for longer forecasts
    std_dev = np.std(y[-30:]) if len(y) >= 30 else np.std(y)
    
    # For longer forecasts, increase uncertainty bounds
    uncertainty_multiplier = min(1.0 + (days / 365.0) * 0.5, 2.0)  # Max 2x uncertainty for 1+ year forecasts
    
    # Get last date
    last_date = data['date'].iloc[-1]
    
    forecasts = []
    for i in range(1, days + 1):
        future_date = last_date + timedelta(days=i)
        
        # Basic linear trend
        predicted_value = y[-1] + (trend * i)
        
        # Add some seasonal-like variation for longer forecasts (simple sine wave)
        if days > 30:
            seasonal_factor = 0.02 * np.sin(2 * np.pi * i / 365)  # Annual seasonality
            predicted_value += seasonal_factor * y[-1]
        
        # Increase uncertainty for longer forecasts
        adjusted_std_dev = std_dev * uncertainty_multiplier * (1 + i / 365.0)
        
        forecast = {
            'ds': future_date.strftime('%Y-%m-%d'),
            'yhat': max(0, predicted_value),  # Ensure non-negative prices
            'yhat_lower': max(0, predicted_value - 1.96 * adjusted_std_dev),
            'yhat_upper': max(0, predicted_value + 1.96 * adjusted_std_dev)
        }
        forecasts.append(forecast)
    
    return forecasts

@app.get("/")
def root():
    return {"message": "Price Forecast API running!"}

# --- Endpoint: View all previous prices ---
@app.get("/history")
def get_history():
    try:
        df = load_data()
        # Return ALL records from the Excel file
        data = df.to_dict(orient="records")
        return clean_data_for_json(data)
    except Exception as e:
        return {"error": f"Failed to load data: {str(e)}"}

# --- Endpoint: View recent prices (limited to 1000 records) ---
@app.get("/history/recent")
def get_recent_history():
    try:
        df = load_data()
        # Limit to recent data to avoid overwhelming response
        df = df.tail(1000)  # Last 1000 records
        data = df.to_dict(orient="records")
        return clean_data_for_json(data)
    except Exception as e:
        return {"error": f"Failed to load data: {str(e)}"}

# --- Endpoint: Get available commodities ---
@app.get("/commodities")
def get_commodities():
    try:
        df = load_data()
        commodities = df['commodity'].unique().tolist()
        return {"commodities": commodities}
    except Exception as e:
        return {"error": f"Failed to load commodities: {str(e)}"}

# --- Endpoint: Forecast for next days (up to 365 days) ---
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
            # Fall back to simple forecasting
            forecasts = simple_forecast(recent_data, days)
            if not forecasts:
                return {"error": f"Both Prophet and simple forecasting failed for '{commodity}'"}
            
            return {"commodity": commodity, "forecast": forecasts, "method": "simple_linear", "prophet_error": str(prophet_error)}
        
    except Exception as e:
        return {"error": f"Failed to generate forecast: {str(e)}"}

# --- Endpoint: Get commodity details ---
@app.get("/commodity/{commodity}")
def get_commodity_details(commodity: str):
    try:
        df = load_data()
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]
        
        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}
        
        # Get basic stats
        stats = {
            "commodity": commodity,
            "total_records": len(filtered),
            "date_range": {
                "earliest": filtered['date'].min().isoformat(),
                "latest": filtered['date'].max().isoformat()
            },
            "price_stats": {
                "min": float(filtered['amount'].min()),
                "max": float(filtered['amount'].max()),
                "avg": float(filtered['amount'].mean()),
                "median": float(filtered['amount'].median())
            },
            "types": filtered['type'].unique().tolist()
        }
        
        return clean_data_for_json(stats)
        
    except Exception as e:
        return {"error": f"Failed to get commodity details: {str(e)}"}

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

# --- Endpoint: Get forecast summary with multiple time horizons ---
@app.get("/forecast-summary/{commodity}")
def forecast_summary(commodity: str):
    try:
        # Get short-term (30 days), medium-term (90 days), and long-term (180 days) forecasts
        short_term = forecast_price(commodity, 30)
        medium_term = forecast_price(commodity, 90)
        long_term = extended_forecast_price(commodity, 6)  # 6 months
        
        return {
            "commodity": commodity,
            "short_term_30_days": short_term,
            "medium_term_90_days": medium_term,
            "long_term_6_months": long_term,
            "summary": {
                "short_term_trend": "Up" if short_term.get('forecast') and len(short_term['forecast']) > 1 and short_term['forecast'][-1]['yhat'] > short_term['forecast'][0]['yhat'] else "Down",
                "medium_term_trend": "Up" if medium_term.get('forecast') and len(medium_term['forecast']) > 1 and medium_term['forecast'][-1]['yhat'] > medium_term['forecast'][0]['yhat'] else "Down",
                "long_term_trend": "Up" if long_term.get('forecast') and len(long_term['forecast']) > 1 and long_term['forecast'][-1]['yhat'] > long_term['forecast'][0]['yhat'] else "Down"
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to generate forecast summary: {str(e)}"}

# --- Endpoint: Get all data statistics ---
@app.get("/data-stats")
def get_data_statistics():
    try:
        df = load_data()
        
        stats = {
            "total_records": len(df),
            "total_commodities": df['commodity'].nunique(),
            "total_types": df['type'].nunique(),
            "date_range": {
                "earliest": df['date'].min().isoformat(),
                "latest": df['date'].max().isoformat()
            },
            "commodities_summary": [],
            "types_summary": []
        }
        
        # Commodity summary
        commodity_counts = df['commodity'].value_counts()
        for commodity, count in commodity_counts.head(10).items():
            stats["commodities_summary"].append({
                "commodity": commodity,
                "record_count": int(count),
                "date_range": {
                    "earliest": df[df['commodity'] == commodity]['date'].min().isoformat(),
                    "latest": df[df['commodity'] == commodity]['date'].max().isoformat()
                }
            })
        
        # Type summary
        type_counts = df['type'].value_counts()
        for type_name, count in type_counts.head(10).items():
            stats["types_summary"].append({
                "type": type_name,
                "record_count": int(count),
                "price_range": {
                    "min": float(df[df['type'] == type_name]['amount'].min()),
                    "max": float(df[df['type'] == type_name]['amount'].max()),
                    "avg": float(df[df['type'] == type_name]['amount'].mean())
                }
            })
        
        return clean_data_for_json(stats)
        
    except Exception as e:
        return {"error": f"Failed to get data statistics: {str(e)}"}

# --- Endpoint: Get all data for a specific commodity ---
@app.get("/commodity/{commodity}/all-data")
def get_commodity_all_data(commodity: str):
    try:
        df = load_data()
        
        # Filter for the commodity
        filtered = df[df['commodity'].str.contains(commodity, case=False, na=False)]
        
        if filtered.empty:
            return {"error": f"No data found for '{commodity}'"}
        
        # Sort by date
        filtered = filtered.sort_values('date')
        
        data = filtered.to_dict(orient="records")
        return clean_data_for_json(data)
        
    except Exception as e:
        return {"error": f"Failed to get commodity data: {str(e)}"}

# --- Endpoint: Get all data for a specific type ---
@app.get("/type/{type_name}/all-data")
def get_type_all_data(type_name: str):
    try:
        df = load_data()
        
        # Filter for the type
        filtered = df[df['type'].str.contains(type_name, case=False, na=False)]
        
        if filtered.empty:
            return {"error": f"No data found for type '{type_name}'"}
        
        # Sort by date
        filtered = filtered.sort_values('date')
        
        data = filtered.to_dict(orient="records")
        return clean_data_for_json(data)
        
    except Exception as e:
        return {"error": f"Failed to get type data: {str(e)}"}

# --- Endpoint: Search data by date range ---
@app.get("/data/date-range/{start_date}/{end_date}")
def get_data_by_date_range(start_date: str, end_date: str):
    try:
        df = load_data()
        
        # Convert string dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter by date range
        filtered = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
        
        if filtered.empty:
            return {"error": f"No data found between {start_date} and {end_date}"}
        
        # Sort by date
        filtered = filtered.sort_values('date')
        
        data = filtered.to_dict(orient="records")
        return clean_data_for_json(data)
        
    except Exception as e:
        return {"error": f"Failed to get data by date range: {str(e)}"}

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

        # Generate daily forecasts first
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
            "method": "enhanced_linear_with_seasonal_adjustment",
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