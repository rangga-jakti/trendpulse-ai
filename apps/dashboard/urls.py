from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('trend/<slug:slug>/', views.trend_detail, name='trend_detail'),
    path('search/', views.search_trends, name='search'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/json/', views.export_json, name='export_json'),
    path('api/topics/', views.api_trending_topics, name='api_topics'),
    path('api/generate-analysis/<int:topic_id>/', views.generate_ai_analysis, name='generate_analysis'),
    path('api/generate-prediction/<int:topic_id>/', views.generate_ml_prediction, name='generate_prediction'),
    path('api/manual-fetch/', views.trigger_manual_fetch, name='manual_fetch'),
]
