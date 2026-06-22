from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    """Endpoint health check untuk Docker/Coolify.
    Return plain 200 OK — tidak cek DB agar tidak gagal saat db.sqlite3 belum ada.
    """
    return HttpResponse("ok", content_type="text/plain", status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
