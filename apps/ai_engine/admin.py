from django.contrib import admin
from .models import AIInsight, ContentIdea

@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['topic', 'overall_sentiment', 'predicted_longevity', 'model_used', 'created_at']

@admin.register(ContentIdea)
class ContentIdeaAdmin(admin.ModelAdmin):
    list_display = ['topic', 'platform', 'title', 'difficulty']
    list_filter = ['platform', 'difficulty']
