from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import logging

logger = logging.getLogger(__name__)

def fetch_trends_job():
    """Auto-fetch trends every 15 minutes"""
    try:
        from apps.trends.services import TrendDataIngestionService
        service = TrendDataIngestionService()
        service.ingest_trending_topics()
        logger.info("Auto fetch trends completed")
    except Exception as e:
        logger.error(f"Auto fetch error: {e}")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        fetch_trends_job,
        'interval',
        minutes=15,
        id='fetch_trends',
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started - fetching trends every 15 minutes")