"""
TrendPulse AI - Virality Scoring Engine
Calculates virality scores using multiple data signals
"""
import logging
import numpy as np
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# Virality weights
WEIGHTS = {
    'search_volume': 0.35,
    'growth_velocity': 0.30,
    'news_coverage': 0.20,
    'momentum': 0.15,
}


class ViralityEngine:
    """
    Calculates virality score for a trending topic.
    
    Formula:
    virality = (
        w1 * normalized_search_volume +
        w2 * growth_velocity +
        w3 * news_coverage_score +
        w4 * momentum_score
    ) * 100
    """
    
    def calculate_score(self, topic):
        """Calculate comprehensive virality score for a topic"""
        from apps.analytics.models import ViralityScore
        
        # Get component scores
        search_volume_score = self._calc_search_volume_score(topic)
        growth_velocity_score = self._calc_growth_velocity_score(topic)
        news_coverage_score = self._calc_news_coverage_score(topic)
        momentum_score = self._calc_momentum_score(topic)
        
        # Weighted sum
        final_score = (
            WEIGHTS['search_volume'] * search_volume_score +
            WEIGHTS['growth_velocity'] * growth_velocity_score +
            WEIGHTS['news_coverage'] * news_coverage_score +
            WEIGHTS['momentum'] * momentum_score
        )
        
        # Clamp to 0-100
        final_score = max(0.0, min(100.0, final_score))
        
        tier = ViralityScore.get_tier_for_score(final_score)
        
        # Save score
        vs = ViralityScore.objects.create(
            topic=topic,
            score=final_score,
            search_volume_score=search_volume_score,
            growth_velocity_score=growth_velocity_score,
            news_coverage_score=news_coverage_score,
            momentum_score=momentum_score,
            tier=tier,
        )
        
        return vs
    
    def _calc_search_volume_score(self, topic):
        """Score based on current search interest (0-100 from Google Trends directly)"""
        return float(topic.current_interest)
    
    def _calc_growth_velocity_score(self, topic):
        """Score based on how fast the trend is growing"""
        growth = topic.growth_rate
        
        if growth <= 0:
            return 0.0
        elif growth >= 500:
            return 100.0
        else:
            # Logarithmic scale for growth
            return min(100.0, (np.log1p(growth) / np.log1p(500)) * 100)
    
    def _calc_news_coverage_score(self, topic):
        """Score based on news article coverage"""
        # Count articles in last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        recent_news_count = topic.news_articles.filter(
            published_at__gte=yesterday
        ).count()
        
        # Scale: 0 articles = 0, 10+ articles = 100
        return min(100.0, recent_news_count * 10.0)
    
    def _calc_momentum_score(self, topic):
        """Score based on sustained growth over time"""
        # Get last 7 data points
        data_points = topic.data_points.order_by('-timestamp')[:14]
        
        if len(data_points) < 4:
            return topic.current_interest  # Fallback
        
        values = [dp.interest_value for dp in reversed(list(data_points))]
        
        if not values:
            return 0.0
        
        # Check if trend is consistently growing
        half = len(values) // 2
        first_half_avg = np.mean(values[:half]) if values[:half] else 0
        second_half_avg = np.mean(values[half:]) if values[half:] else 0
        
        if first_half_avg == 0:
            return second_half_avg
        
        momentum_ratio = second_half_avg / first_half_avg
        
        # If growing (>1.0), boost score. If declining, reduce.
        if momentum_ratio >= 2.0:
            return 100.0
        elif momentum_ratio >= 1.0:
            return (momentum_ratio - 1.0) * 100.0
        else:
            return max(0.0, momentum_ratio * 50.0)


class ViralityAnalytics:
    """Provides analytics views and aggregations for virality data"""
    
    def get_top_viral_topics(self, limit=10):
        """Get top viral topics right now"""
        from apps.trends.models import TrendTopic
        from apps.analytics.models import ViralityScore
        
        # Get the latest score for each topic
        latest_scores = ViralityScore.objects.order_by(
            'topic', '-calculated_at'
        ).distinct('topic').select_related('topic')
        
        return sorted(latest_scores, key=lambda x: x.score, reverse=True)[:limit]
    
    def get_virality_distribution(self):
        """Get distribution of virality tiers"""
        from apps.analytics.models import ViralityScore
        from django.db.models import Count
        
        return ViralityScore.objects.order_by(
            'topic', '-calculated_at'
        ).distinct('topic').values('tier').annotate(count=Count('tier'))
