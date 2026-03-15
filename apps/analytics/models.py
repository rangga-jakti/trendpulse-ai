from django.db import models
from django.utils import timezone


class ViralityScore(models.Model):
    """Calculated virality score for a trending topic"""
    
    topic = models.ForeignKey(
        'trends.TrendTopic',
        on_delete=models.CASCADE,
        related_name='virality_scores'
    )
    
    # Overall score (0-100)
    score = models.FloatField(default=0.0)
    
    # Component scores
    search_volume_score = models.FloatField(default=0.0, help_text='Based on raw search interest')
    growth_velocity_score = models.FloatField(default=0.0, help_text='Speed of growth')
    news_coverage_score = models.FloatField(default=0.0, help_text='News article coverage')
    momentum_score = models.FloatField(default=0.0, help_text='Sustained growth momentum')
    
    # Virality tier
    TIER_CHOICES = [
        ('mega', 'Mega Viral (90-100)'),
        ('high', 'Sangat Viral (70-89)'),
        ('medium', 'Viral (50-69)'),
        ('low', 'Mulai Viral (30-49)'),
        ('minimal', 'Belum Viral (0-29)'),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='minimal')
    
    calculated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Skor Viralitas'
    
    def __str__(self):
        return f"{self.topic.keyword}: {self.score:.1f}"
    
    @classmethod
    def get_tier_for_score(cls, score):
        if score >= 90:
            return 'mega'
        elif score >= 70:
            return 'high'
        elif score >= 50:
            return 'medium'
        elif score >= 30:
            return 'low'
        return 'minimal'
