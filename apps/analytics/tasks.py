from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def calculate_all_virality_scores():
    """Calculate virality scores for all active topics"""
    from apps.trends.models import TrendTopic
    from apps.analytics.services import ViralityEngine
    
    engine = ViralityEngine()
    active_topics = TrendTopic.objects.filter(is_active=True)
    
    count = 0
    for topic in active_topics:
        try:
            engine.calculate_score(topic)
            count += 1
        except Exception as e:
            logger.error(f"Virality score error for {topic.keyword}: {e}")
    
    return {'status': 'success', 'scored': count}


@shared_task
def calculate_virality_for_topic(topic_id):
    """Calculate virality score for a specific topic"""
    from apps.trends.models import TrendTopic
    from apps.analytics.services import ViralityEngine
    
    try:
        topic = TrendTopic.objects.get(id=topic_id)
        engine = ViralityEngine()
        score = engine.calculate_score(topic)
        return {'status': 'success', 'score': score.score}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
