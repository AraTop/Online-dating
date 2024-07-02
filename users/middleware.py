from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import User

class UpdateLastActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(
                last_activity=timezone.now(), is_online=True
            )