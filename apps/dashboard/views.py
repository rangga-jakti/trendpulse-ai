"""
TrendPulse AI - Dashboard Views
Main views for the dashboard and trend detail pages
"""
import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

def dashboard(request):
    """Main dashboard view"""
    from apps.trends.models import TrendTopic, NewsArticle
    from apps.analytics.models import ViralityScore
    from django.db.models import Avg, Count

    # Fetch active trending topics
    trending_topics = TrendTopic.objects.filter(
        is_active=True
    ).order_by('-current_interest')[:50]

    # Breaking trends (high growth rate)
    breaking_trends = TrendTopic.objects.filter(
        is_active=True, is_breaking=True
    ).order_by('-growth_rate')[:6]

    # Recent news
    recent_news = NewsArticle.objects.order_by('-published_at')[:10]

    # Summary stats
    total_trends = TrendTopic.objects.filter(is_active=True).count()
    avg_growth = TrendTopic.objects.filter(
        is_active=True, growth_rate__gt=0
    ).aggregate(avg=Avg('growth_rate'))['avg'] or 0

    # Top viral topics - get latest score per topic
    top_viral = []
    try:
        from apps.analytics.models import ViralityScore
        # Get topics with their latest virality scores
        scored_topics = TrendTopic.objects.filter(
            is_active=True,
            virality_scores__isnull=False
        ).distinct()

        viral_list = []
        for topic in scored_topics:
            latest = topic.virality_scores.order_by('-calculated_at').first()
            if latest:
                viral_list.append(latest)

        top_viral = sorted(viral_list, key=lambda x: x.score, reverse=True)[:8]
    except Exception as e:
        logger.error(f"Error getting viral topics: {e}")

    context = {
        'trending_topics': trending_topics,
        'breaking_trends': breaking_trends,
        'recent_news': recent_news,
        'top_viral': top_viral,
        'total_trends': total_trends,
        'avg_growth': round(avg_growth, 1),
        'last_updated': timezone.now(),
        'breaking_count': breaking_trends.count(),
    }

    return render(request, 'dashboard/index.html', context)


@login_required
def trend_detail(request, slug):
    """Trend detail page with full AI analysis"""
    topic = get_object_or_404(
        __import__('apps.trends.models', fromlist=['TrendTopic']).TrendTopic,
        slug=slug
    )
    
    # Get or trigger AI insight
    from apps.ai_engine.models import AIInsight, ContentIdea
    from apps.ml_engine.models import MLPrediction
    
    ai_insight = topic.ai_insights.first()
    ml_prediction = topic.predictions.first()
    content_ideas = topic.content_ideas.all()
    news_articles = topic.news_articles.order_by('-published_at')[:8]
    
    # Historical data for chart
    data_points = list(
        topic.data_points.order_by('timestamp').values('timestamp', 'interest_value')
    )
    
    chart_data = {
        'labels': [str(dp['timestamp'].strftime('%d %b') if hasattr(dp['timestamp'], 'strftime') else dp['timestamp']) for dp in data_points],
        'values': [dp['interest_value'] for dp in data_points],
    }
    
    # Prediction chart data
    prediction_chart = {}
    if ml_prediction and ml_prediction.forecast_30d:
        prediction_chart = ml_prediction.forecast_7d_chart_data
    
    context = {
        'topic': topic,
        'ai_insight': ai_insight,
        'ml_prediction': ml_prediction,
        'content_ideas': content_ideas,
        'news_articles': news_articles,
        'chart_data': json.dumps(chart_data),
        'prediction_chart': json.dumps(prediction_chart),
        'virality_score': topic.virality_score,
        'platforms': ['youtube', 'tiktok', 'blog', 'business'],
    }
    
    return render(request, 'dashboard/trend_detail.html', context)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(['POST'])
def generate_ai_analysis(request, topic_id):
    """HTMX endpoint: generate AI analysis for a topic"""
    from apps.trends.models import TrendTopic
    from apps.ai_engine.services import LLMService
    from apps.ai_engine.models import AIInsight, ContentIdea
    
    try:
        topic = TrendTopic.objects.get(id=topic_id)
        llm = LLMService()
        
        # Get news context
        news_articles = list(topic.news_articles.order_by('-published_at')[:5])
        
        # Get virality score
        virality_score = topic.virality_score
        
        # Generate analysis
        analysis_data = llm.analyze_trend(topic, virality_score, news_articles)
        
        if not analysis_data:
            return JsonResponse({'error': 'LLM tidak tersedia'}, status=500)
        
        # Save insight
        insight = AIInsight.objects.create(
            topic=topic,
            why_trending=analysis_data.get('why_trending', ''),
            potential_impact=analysis_data.get('potential_impact', ''),
            target_audience=analysis_data.get('target_audience', ''),
            predicted_longevity=analysis_data.get('predicted_longevity', 'days'),
            overall_sentiment=analysis_data.get('overall_sentiment', 'neutral'),
            model_used=analysis_data.get('model_used', 'unknown'),
            tokens_used=analysis_data.get('tokens_used', 0),
        )
        
        # Generate content ideas
        content_data = llm.generate_content_ideas(topic, analysis_data)
        
        for platform_key, ideas in content_data.items():
            if platform_key not in ['youtube', 'tiktok', 'blog', 'business']:
                continue
            for idea in (ideas or []):
                try:
                    ContentIdea.objects.create(
                        topic=topic,
                        platform=platform_key,
                        title=idea.get('title', '')[:500],
                        description=idea.get('description', ''),
                        hooks=idea.get('hooks', []),
                        estimated_reach=idea.get('estimated_reach', ''),
                        difficulty=idea.get('difficulty', 'medium'),
                    )
                except Exception as e:
                    logger.error(f"Error saving content idea: {e}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'partials/ai_insight_panel.html', {
                'insight': insight,
                'topic': topic,
                'content_ideas': ContentIdea.objects.filter(topic=topic),
            })
        
        return JsonResponse({'status': 'success', 'insight_id': insight.id})
    
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        if request.htmx:
            return render(request, 'partials/error_panel.html', {'error': str(e)})
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def generate_ml_prediction(request, topic_id):
    """HTMX endpoint: run ML prediction for a topic"""
    from apps.trends.models import TrendTopic
    from apps.ml_engine.services import ProphetForecaster
    
    try:
        topic = TrendTopic.objects.get(id=topic_id)
        forecaster = ProphetForecaster()
        prediction = forecaster.forecast_topic(topic)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'partials/prediction_panel.html', {
                'prediction': prediction,
                'topic': topic,
                'chart_data': json.dumps(prediction.forecast_7d_chart_data) if prediction else '{}',
            })
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error generating ML prediction: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def api_trending_topics(request):
    """JSON API: get trending topics for live updates"""
    from apps.trends.models import TrendTopic
    
    topics = TrendTopic.objects.filter(is_active=True).order_by('-current_interest')[:15]
    
    data = [{
        'id': t.id,
        'keyword': t.keyword,
        'slug': t.slug,
        'current_interest': t.current_interest,
        'growth_rate': t.growth_rate,
        'virality_score': t.virality_score,
        'is_breaking': t.is_breaking,
        'category': t.get_category_display(),
    } for t in topics]
    
    return JsonResponse({'topics': data, 'timestamp': timezone.now().isoformat()})


def trigger_manual_fetch(request):
    """Manually trigger data fetch (for demo/dev purposes)"""
    if request.method == 'POST':
        from apps.trends.tasks import fetch_google_trends, fetch_news_articles
        fetch_google_trends.delay()
        fetch_news_articles.delay()
        return JsonResponse({'status': 'Pengambilan data dimulai di background'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def search_trends(request):
    """Search & filter trends API"""
    from apps.trends.models import TrendTopic
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'interest')
    min_growth = request.GET.get('min_growth', '')

    topics = TrendTopic.objects.filter(is_active=True)

    if q:
        topics = topics.filter(Q(keyword__icontains=q) | Q(category__icontains=q))
    if category:
        topics = topics.filter(category=category)
    if min_growth:
        try:
            topics = topics.filter(growth_rate__gte=float(min_growth))
        except ValueError:
            pass

    if sort == 'growth':
        topics = topics.order_by('-growth_rate')
    elif sort == 'breaking':
        topics = topics.order_by('-is_breaking', '-growth_rate')
    else:
        topics = topics.order_by('-current_interest')

    topics = topics[:50]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'partials/trend_list.html', {'trending_topics': topics})

    return JsonResponse({
        'topics': [{'id': t.id, 'keyword': t.keyword, 'slug': t.slug,
                    'current_interest': t.current_interest, 'growth_rate': t.growth_rate,
                    'is_breaking': t.is_breaking} for t in topics]
    })


def export_csv(request):
    """Export trending topics as CSV"""
    import csv
    from django.http import HttpResponse
    from apps.trends.models import TrendTopic

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="trendpulse-export.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8

    writer = csv.writer(response)
    writer.writerow(['Keyword', 'Kategori', 'Sumber', 'Interest Score', 'Growth Rate (%)',
                     'Virality Score', 'Breaking', 'Pertama Terdeteksi', 'Diperbarui'])

    topics = TrendTopic.objects.filter(is_active=True).order_by('-current_interest')
    for t in topics:
        vs = t.virality_scores.order_by('-calculated_at').first()
        writer.writerow([
            t.keyword,
            t.get_category_display(),
            t.source,
            t.current_interest,
            f"{t.growth_rate:+.1f}",
            f"{vs.score:.0f}" if vs else '-',
            'Ya' if t.is_breaking else 'Tidak',
            t.first_detected.strftime('%d/%m/%Y %H:%M') if t.first_detected else '-',
            t.last_updated.strftime('%d/%m/%Y %H:%M') if t.last_updated else '-',
        ])

    return response


def export_json(request):
    """Export trending topics as JSON"""
    from apps.trends.models import TrendTopic

    topics = TrendTopic.objects.filter(is_active=True).order_by('-current_interest')
    data = []
    for t in topics:
        vs = t.virality_scores.order_by('-calculated_at').first()
        data.append({
            'keyword': t.keyword,
            'category': t.get_category_display(),
            'source': t.source,
            'interest_score': t.current_interest,
            'growth_rate': t.growth_rate,
            'virality_score': vs.score if vs else None,
            'is_breaking': t.is_breaking,
            'first_detected': t.first_detected.isoformat() if t.first_detected else None,
            'last_updated': t.last_updated.isoformat() if t.last_updated else None,
        })

    return JsonResponse({'trends': data, 'total': len(data),
                         'exported_at': timezone.now().isoformat()})