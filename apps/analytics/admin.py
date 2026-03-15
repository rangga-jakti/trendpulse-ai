from django.contrib import admin
from .models import ViralityScore

@admin.register(ViralityScore)
class ViralityScoreAdmin(admin.ModelAdmin):
    list_display = ['topic', 'score', 'tier', 'calculated_at']
    list_filter = ['tier']
    ordering = ['-score']
