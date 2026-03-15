from django.contrib import admin
from .models import MLPrediction

@admin.register(MLPrediction)
class MLPredictionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'trend_direction', 'predicted_peak', 'confidence_score', 'model_type', 'created_at']
    list_filter = ['trend_direction', 'model_type']
