from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Endpoint health check untuk Docker dan load balancer."""
    try:
        # Cek koneksi database
        connection.ensure_connection()
        return JsonResponse({'status': 'ok', 'database': 'ok'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=503)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
