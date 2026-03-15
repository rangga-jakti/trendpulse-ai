from django.contrib import admin
from .models import TrendTopic, TrendDataPoint, NewsArticle

@admin.register(TrendTopic)
class TrendTopicAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'category', 'current_interest', 'growth_rate', 'is_active', 'is_breaking', 'last_updated']
    list_filter = ['category', 'is_active', 'is_breaking', 'source']
    search_fields = ['keyword']
    ordering = ['-current_interest']

@admin.register(TrendDataPoint)
class TrendDataPointAdmin(admin.ModelAdmin):
    list_display = ['topic', 'timestamp', 'interest_value']
    list_filter = ['topic']

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_name', 'published_at', 'topic']
    search_fields = ['title']
