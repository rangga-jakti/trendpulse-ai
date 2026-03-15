from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),
    path('trends/', include('apps.trends.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('ai/', include('apps.ai_engine.urls')),
    path('ml/', include('apps.ml_engine.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)