from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_predictions_for_active_trends():
    """Run ML predictions for all active trending topics"""
    from apps.trends.models import TrendTopic
    from apps.ml_engine.services import ProphetForecaster
    
    forecaster = ProphetForecaster()
    active_topics = TrendTopic.objects.filter(is_active=True)
    
    count = 0
    for topic in active_topics:
        try:
            prediction = forecaster.forecast_topic(topic)
            if prediction:
                count += 1
        except Exception as e:
            logger.error(f"Prediction error for {topic.keyword}: {e}")
    
    return {'status': 'success', 'predictions': count}


@shared_task
def run_prediction_for_topic(topic_id):
    """Run ML prediction for a specific topic (triggered on demand)"""
    from apps.trends.models import TrendTopic
    from apps.ml_engine.services import ProphetForecaster
    
    try:
        topic = TrendTopic.objects.get(id=topic_id)
        forecaster = ProphetForecaster()
        prediction = forecaster.forecast_topic(topic)
        return {
            'status': 'success',
            'topic': topic.keyword,
            'direction': prediction.trend_direction if prediction else 'unknown',
        }
    except Exception as e:
        logger.error(f"Prediction task error: {e}")
        return {'status': 'error', 'message': str(e)}
