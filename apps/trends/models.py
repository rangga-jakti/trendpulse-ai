from django.db import models
from django.utils import timezone


class TrendTopic(models.Model):
    """Represents a trending topic detected from Google Trends or News"""
    
    CATEGORY_CHOICES = [
        ('technology', 'Teknologi'),
        ('business', 'Bisnis'),
        ('entertainment', 'Hiburan'),
        ('sports', 'Olahraga'),
        ('politics', 'Politik'),
        ('science', 'Sains'),
        ('health', 'Kesehatan'),
        ('general', 'Umum'),
    ]
    
    SOURCE_CHOICES = [
        ('google_trends', 'Google Trends'),
        ('news_api', 'News API'),
        ('combined', 'Gabungan'),
    ]

    keyword = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='google_trends')
    
    # Current metrics
    current_interest = models.FloatField(default=0.0, help_text='0-100 scale from Google Trends')
    peak_interest = models.FloatField(default=0.0)
    growth_rate = models.FloatField(default=0.0, help_text='Percentage growth in last 24h')
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_breaking = models.BooleanField(default=False, help_text='Sudden spike detected')
    
    # Timestamps
    first_detected = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-current_interest', '-last_updated']
        verbose_name = 'Topik Tren'
        verbose_name_plural = 'Topik-Topik Tren'
    
    def __str__(self):
        return self.keyword
    
    @property
    def virality_score(self):
        try:
            return self.virality_scores.latest('calculated_at').score
        except Exception:
            return 0.0
    
    @property
    def latest_prediction(self):
        try:
            return self.predictions.latest('created_at')
        except Exception:
            return None


class TrendDataPoint(models.Model):
    """Time-series data points for a trend topic"""
    
    topic = models.ForeignKey(TrendTopic, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField(db_index=True)
    interest_value = models.FloatField(help_text='Interest value 0-100')
    news_count = models.IntegerField(default=0, help_text='Number of news articles at this time')
    
    class Meta:
        ordering = ['timestamp']
        unique_together = ['topic', 'timestamp']
        verbose_name = 'Data Point Tren'
    
    def __str__(self):
        return f"{self.topic.keyword} @ {self.timestamp}: {self.interest_value}"


class NewsArticle(models.Model):
    """News articles related to trending topics"""
    
    topic = models.ForeignKey(
        TrendTopic, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='news_articles'
    )
    title = models.TextField()
    description = models.TextField(blank=True)
    url = models.URLField(max_length=1000, unique=True)
    source_name = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    sentiment_score = models.FloatField(default=0.0, help_text='-1 negative, 0 neutral, 1 positive')
    relevance_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Artikel Berita'
    
    def __str__(self):
        return self.title[:80]
