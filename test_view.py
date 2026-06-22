import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_ddshoes.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.views import closing_admin

factory = RequestFactory()
request = factory.get('/closing-admin/')
request.user = User.objects.filter(userprofile__role='admin').first()

try:
    response = closing_admin(request)
    print("STATUS_CODE:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
