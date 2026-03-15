"""
Django management command to manually trigger trend fetching.
Usage: python manage.py fetch_trends
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fetch trending topics from Google Trends and NewsAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo', action='store_true',
            help='Create demo data instead of fetching real data (for testing without API keys)'
        )

    def handle(self, *args, **options):
        if options['demo']:
            self._create_demo_data()
            return
        
        self.stdout.write('🔍 Memulai pengambilan data tren...')
        
        try:
            from apps.trends.services import TrendDataIngestionService
            service = TrendDataIngestionService()
            count = service.ingest_trending_topics()
            self.stdout.write(self.style.SUCCESS(f'✅ Berhasil mengambil {count} topik tren'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            
        # Calculate virality scores
        self.stdout.write('📊 Menghitung skor viralitas...')
        try:
            from apps.trends.models import TrendTopic
            from apps.analytics.services import ViralityEngine
            engine = ViralityEngine()
            for topic in TrendTopic.objects.filter(is_active=True):
                try:
                    engine.calculate_score(topic)
                except Exception as e:
                    self.stdout.write(f'  Warning for {topic.keyword}: {e}')
            self.stdout.write(self.style.SUCCESS('✅ Skor viralitas dihitung'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error virality: {e}'))

    def _create_demo_data(self):
        """Create realistic demo data for testing without API keys"""
        from django.utils.text import slugify
        from apps.trends.models import TrendTopic, TrendDataPoint, NewsArticle
        from apps.analytics.services import ViralityEngine
        import random
        from datetime import timedelta
        
        self.stdout.write('🎭 Membuat demo data...')
        
        demo_trends = [
            {'keyword': 'Kecerdasan Buatan Indonesia', 'category': 'technology', 'interest': 85, 'growth': 245},
            {'keyword': 'ChatGPT Bahasa Indonesia', 'category': 'technology', 'interest': 92, 'growth': 312},
            {'keyword': 'Rupiah Digital', 'category': 'business', 'interest': 78, 'growth': 189},
            {'keyword': 'IKN Nusantara', 'category': 'politics', 'interest': 67, 'growth': 45},
            {'keyword': 'Mudik Lebaran 2025', 'category': 'general', 'interest': 95, 'growth': 520},
            {'keyword': 'Film Indonesia Terbaru', 'category': 'entertainment', 'interest': 72, 'growth': 134},
            {'keyword': 'Timnas Garuda', 'category': 'sports', 'interest': 88, 'growth': 276},
            {'keyword': 'Startup Unicorn Baru', 'category': 'business', 'interest': 61, 'growth': 98},
            {'keyword': 'Vaksin Dengue', 'category': 'health', 'interest': 74, 'growth': 167},
            {'keyword': 'Baterai Kendaraan Listrik', 'category': 'technology', 'interest': 69, 'growth': 123},
        ]
        
        engine = ViralityEngine()
        now = timezone.now()
        
        for trend_data in demo_trends:
            topic, created = TrendTopic.objects.update_or_create(
                keyword=trend_data['keyword'],
                defaults={
                    'slug': slugify(trend_data['keyword']),
                    'category': trend_data['category'],
                    'source': 'google_trends',
                    'current_interest': trend_data['interest'],
                    'peak_interest': trend_data['interest'] * 1.1,
                    'growth_rate': trend_data['growth'],
                    'is_active': True,
                    'is_breaking': trend_data['growth'] > 200,
                }
            )
            
            # Create historical data points (90 days)
            for i in range(90, 0, -1):
                ts = now - timedelta(days=i)
                base = trend_data['interest'] * (1 - i/90 * 0.6)
                noise = random.uniform(-5, 8)
                value = max(0, min(100, base + noise))
                
                TrendDataPoint.objects.get_or_create(
                    topic=topic,
                    timestamp=ts.replace(hour=0, minute=0, second=0, microsecond=0),
                    defaults={'interest_value': value}
                )
            
            # Calculate virality
            try:
                engine.calculate_score(topic)
            except Exception as e:
                pass
            
            action = 'Dibuat' if created else 'Diperbarui'
            self.stdout.write(f'  ✓ {action}: {topic.keyword}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Demo data berhasil dibuat: {len(demo_trends)} topik dengan 90 hari data historis'))
        self.stdout.write(self.style.WARNING('\n⚠️  Ini adalah data demo. Untuk data real, konfigurasi API keys di .env'))
