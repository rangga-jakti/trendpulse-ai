from django.db import models
from django.utils import timezone


class AIInsight(models.Model):
    """AI-generated analysis of a trending topic"""
    
    topic = models.ForeignKey(
        'trends.TrendTopic',
        on_delete=models.CASCADE,
        related_name='ai_insights'
    )
    
    # AI Analysis
    why_trending = models.TextField(help_text='AI explanation of why this is trending')
    potential_impact = models.TextField(help_text='Potential impact analysis')
    target_audience = models.TextField(blank=True)
    predicted_longevity = models.CharField(
        max_length=50,
        choices=[
            ('hours', 'Beberapa Jam'),
            ('days', 'Beberapa Hari'),
            ('weeks', 'Beberapa Minggu'),
            ('months', 'Beberapa Bulan'),
            ('permanent', 'Jangka Panjang'),
        ],
        default='days'
    )
    
    # Sentiment
    overall_sentiment = models.CharField(
        max_length=20,
        choices=[('positive', 'Positif'), ('neutral', 'Netral'), ('negative', 'Negatif')],
        default='neutral'
    )
    
    # Metadata
    model_used = models.CharField(max_length=100, default='llama3-70b-8192')
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wawasan AI'
    
    def __str__(self):
        return f"Insight: {self.topic.keyword} ({self.created_at.strftime('%d/%m/%Y')})"


class ContentIdea(models.Model):
    """AI-generated content ideas for a trend"""
    
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('blog', 'Blog/Artikel'),
        ('business', 'Peluang Bisnis'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
    ]
    
    topic = models.ForeignKey(
        'trends.TrendTopic',
        on_delete=models.CASCADE,
        related_name='content_ideas'
    )
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    title = models.CharField(max_length=500)
    description = models.TextField()
    hooks = models.JSONField(default=list, help_text='List of attention hooks/angles')
    estimated_reach = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Mudah'), ('medium', 'Sedang'), ('hard', 'Sulit')],
        default='medium'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['platform', '-created_at']
        verbose_name = 'Ide Konten'
    
    def __str__(self):
        return f"{self.get_platform_display()}: {self.title[:60]}"
