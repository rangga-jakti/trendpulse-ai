from django.db import models
from django.utils import timezone
import json


class MLPrediction(models.Model):
    """Machine Learning prediction for a trend topic"""
    
    topic = models.ForeignKey(
        'trends.TrendTopic',
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    
    # Forecast data (stored as JSON)
    forecast_7d = models.JSONField(default=list, help_text='7-day forecast: [{date, value, lower, upper}]')
    forecast_30d = models.JSONField(default=list, help_text='30-day forecast')
    
    # Summary metrics
    predicted_peak = models.FloatField(default=0.0)
    predicted_peak_date = models.DateTimeField(null=True, blank=True)
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('rising', 'Naik'),
            ('stable', 'Stabil'),
            ('declining', 'Turun'),
            ('volatile', 'Volatile'),
        ],
        default='stable'
    )
    confidence_score = models.FloatField(default=0.0, help_text='Model confidence 0-1')
    
    # Model info
    model_type = models.CharField(max_length=50, default='prophet')
    training_data_points = models.IntegerField(default=0)
    mae = models.FloatField(default=0.0, help_text='Mean Absolute Error')
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediksi ML'
    
    def __str__(self):
        return f"Prediksi {self.topic.keyword}: {self.trend_direction} (conf: {self.confidence_score:.2f})"
    
    @property
    def forecast_7d_chart_data(self):
        """Format 7d forecast for Chart.js"""
        return {
            'labels': [p['date'] for p in self.forecast_7d],
            'values': [p['value'] for p in self.forecast_7d],
            'lower': [p.get('lower', 0) for p in self.forecast_7d],
            'upper': [p.get('upper', 100) for p in self.forecast_7d],
        }
