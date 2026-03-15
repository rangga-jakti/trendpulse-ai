"""
TrendPulse AI - Machine Learning Forecasting Service
Uses Prophet for time-series trend prediction
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProphetForecaster:
    """Time-series forecasting using Facebook Prophet"""
    
    def forecast_topic(self, topic, forecast_days=30):
        """
        Generate forecast for a trend topic using Prophet.
        Returns MLPrediction object or None.
        """
        from apps.ml_engine.models import MLPrediction
        
        # Get historical data
        data_points = topic.data_points.order_by('timestamp')
        
        if data_points.count() < 10:
            logger.warning(f"Not enough data for {topic.keyword}: {data_points.count()} points")
            return self._simple_forecast(topic, forecast_days)
        
        # Prepare DataFrame for Prophet
        df = pd.DataFrame([
            {'ds': dp.timestamp, 'y': dp.interest_value}
            for dp in data_points
        ])
        
        # Ensure timezone-naive timestamps
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
        df = df.dropna()
        df = df.sort_values('ds').drop_duplicates('ds')
        
        if len(df) < 10:
            return self._simple_forecast(topic, forecast_days)
        
        try:
            from prophet import Prophet
            
            model = Prophet(
                changepoint_prior_scale=0.15,
                seasonality_mode='multiplicative',
                interval_width=0.80,
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
            )
            
            # Add custom seasonality for news cycles
            model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_days, freq='D')
            forecast = model.predict(future)
            
            # Extract forecast for future dates only
            future_forecast = forecast[forecast['ds'] > df['ds'].max()].head(forecast_days)
            
            # Build 7-day and 30-day forecast data
            forecast_7d = []
            forecast_30d = []
            
            for _, row in future_forecast.iterrows():
                point = {
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'value': max(0.0, float(row['yhat'])),
                    'lower': max(0.0, float(row['yhat_lower'])),
                    'upper': min(100.0, float(row['yhat_upper'])),
                }
                forecast_30d.append(point)
                if len(forecast_7d) < 7:
                    forecast_7d.append(point)
            
            # Calculate metrics
            if len(forecast_30d) > 0:
                values = [p['value'] for p in forecast_30d]
                predicted_peak = max(values)
                peak_idx = values.index(predicted_peak)
                peak_date = datetime.strptime(forecast_30d[peak_idx]['date'], '%Y-%m-%d')
                
                # Trend direction
                if len(values) >= 7:
                    first_half = np.mean(values[:len(values)//2])
                    second_half = np.mean(values[len(values)//2:])
                    growth = (second_half - first_half) / (first_half + 1e-10)
                    
                    if growth > 0.15:
                        direction = 'rising'
                    elif growth < -0.15:
                        direction = 'declining'
                    elif np.std(values) / (np.mean(values) + 1e-10) > 0.3:
                        direction = 'volatile'
                    else:
                        direction = 'stable'
                else:
                    direction = 'stable'
            else:
                predicted_peak = topic.current_interest
                peak_date = timezone.now() + timedelta(days=7)
                direction = 'stable'
            
            # Calculate MAE on training data
            train_forecast = forecast[forecast['ds'] <= df['ds'].max()]
            mae = float(np.mean(np.abs(train_forecast['yhat'].values - df['y'].values[:len(train_forecast)])))
            confidence = max(0.0, min(1.0, 1.0 - (mae / 100.0)))
            
            # Save prediction
            prediction = MLPrediction.objects.create(
                topic=topic,
                forecast_7d=forecast_7d,
                forecast_30d=forecast_30d,
                predicted_peak=predicted_peak,
                predicted_peak_date=timezone.make_aware(peak_date),
                trend_direction=direction,
                confidence_score=confidence,
                model_type='prophet',
                training_data_points=len(df),
                mae=mae,
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prophet forecasting error for {topic.keyword}: {e}")
            return self._simple_forecast(topic, forecast_days)
    
    def _simple_forecast(self, topic, forecast_days=30):
        """Fallback: simple linear regression forecast"""
        from apps.ml_engine.models import MLPrediction
        from sklearn.linear_model import LinearRegression
        
        data_points = list(topic.data_points.order_by('timestamp')[:30])
        
        if not data_points:
            # No data at all - create placeholder
            return self._placeholder_forecast(topic, forecast_days)
        
        values = [dp.interest_value for dp in data_points]
        X = np.arange(len(values)).reshape(-1, 1)
        y = np.array(values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast
        future_X = np.arange(len(values), len(values) + forecast_days).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        start_date = datetime.now() + timedelta(days=1)
        forecast_7d = []
        forecast_30d = []
        
        for i, pred in enumerate(predictions):
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            value = max(0.0, min(100.0, float(pred)))
            std = np.std(values) if len(values) > 1 else 5.0
            point = {
                'date': date,
                'value': value,
                'lower': max(0.0, value - std),
                'upper': min(100.0, value + std),
            }
            forecast_30d.append(point)
            if i < 7:
                forecast_7d.append(point)
        
        slope = model.coef_[0]
        if slope > 0.5:
            direction = 'rising'
        elif slope < -0.5:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return MLPrediction.objects.create(
            topic=topic,
            forecast_7d=forecast_7d,
            forecast_30d=forecast_30d,
            predicted_peak=max([p['value'] for p in forecast_30d]) if forecast_30d else topic.current_interest,
            trend_direction=direction,
            confidence_score=0.6,
            model_type='linear_regression',
            training_data_points=len(data_points),
            mae=float(np.mean(np.abs(model.predict(X) - y))),
        )
    
    def _placeholder_forecast(self, topic, forecast_days=30):
        """Create a placeholder prediction when no data is available"""
        from apps.ml_engine.models import MLPrediction
        
        base_value = topic.current_interest or 50.0
        start_date = datetime.now() + timedelta(days=1)
        
        forecast_7d = []
        forecast_30d = []
        
        for i in range(forecast_days):
            value = base_value * (1 + topic.growth_rate / 100 * 0.1 * (1 - i/30))
            value = max(0.0, min(100.0, value))
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            point = {
                'date': date,
                'value': value,
                'lower': max(0.0, value - 10),
                'upper': min(100.0, value + 10),
            }
            forecast_30d.append(point)
            if i < 7:
                forecast_7d.append(point)
        
        return MLPrediction.objects.create(
            topic=topic,
            forecast_7d=forecast_7d,
            forecast_30d=forecast_30d,
            predicted_peak=base_value,
            trend_direction='stable',
            confidence_score=0.3,
            model_type='heuristic',
            training_data_points=0,
        )
