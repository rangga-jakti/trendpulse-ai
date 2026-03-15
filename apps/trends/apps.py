from django.apps import AppConfig

class TrendsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trends'
    verbose_name = 'Trends'

    def ready(self):
        from apps.trends import scheduler
        scheduler.start()