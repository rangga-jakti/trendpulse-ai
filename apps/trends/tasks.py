from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_google_trends(self):
    """Celery task: fetch trending topics from Google Trends"""
    try:
        from apps.trends.services import TrendDataIngestionService
        service = TrendDataIngestionService()
        count = service.ingest_trending_topics()
        logger.info(f"Successfully fetched {count} trending topics")
        return {'status': 'success', 'count': count}
    except Exception as exc:
        logger.error(f"Error in fetch_google_trends task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_news_articles(self):
    """Celery task: fetch news articles"""
    try:
        from apps.trends.services import NewsAPIService
        from apps.trends.models import TrendTopic, NewsArticle
        
        news_service = NewsAPIService()
        active_topics = TrendTopic.objects.filter(is_active=True)[:10]
        
        count = 0
        for topic in active_topics:
            articles = news_service.search_news_for_keyword(topic.keyword)
            for article in articles:
                if not article.get('url') or not article.get('title'):
                    continue
                try:
                    from dateutil import parser as dateparser
                    from django.utils import timezone
                    published_at = dateparser.parse(article['publishedAt']) if article.get('publishedAt') else timezone.now()
                    
                    obj, created = NewsArticle.objects.get_or_create(
                        url=article['url'][:1000],
                        defaults={
                            'topic': topic,
                            'title': article.get('title', '')[:500],
                            'description': article.get('description', '') or '',
                            'source_name': (article.get('source', {}) or {}).get('name', 'Unknown'),
                            'published_at': published_at,
                        }
                    )
                    if created:
                        count += 1
                except Exception as e:
                    logger.error(f"Error saving article: {e}")
        
        logger.info(f"Saved {count} new news articles")
        return {'status': 'success', 'count': count}
    except Exception as exc:
        logger.error(f"Error in fetch_news_articles task: {exc}")
        raise self.retry(exc=exc)


@shared_task
def fetch_trend_detail(topic_id):
    """Fetch detailed data for a specific trend topic"""
    try:
        from apps.trends.models import TrendTopic
        from apps.trends.services import GoogleTrendsService
        
        topic = TrendTopic.objects.get(id=topic_id)
        service = GoogleTrendsService()
        
        # Get interest over time (last 3 months)
        data = service.fetch_interest_over_time([topic.keyword])
        
        if topic.keyword in data:
            from apps.trends.models import TrendDataPoint
            for timestamp, value in data[topic.keyword].items():
                if isinstance(value, (int, float)) and value > 0:
                    TrendDataPoint.objects.get_or_create(
                        topic=topic,
                        timestamp=timestamp,
                        defaults={'interest_value': float(value)}
                    )
        
        return {'status': 'success', 'topic': topic.keyword}
    except Exception as e:
        logger.error(f"Error fetching trend detail: {e}")
        return {'status': 'error', 'message': str(e)}
