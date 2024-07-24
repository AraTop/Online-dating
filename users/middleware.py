from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class UserOnlineStatusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if request.path == '/users/logout/':
                # Обработка выхода из системы
                user = request.user
                user.is_online = False
                user.save()
            else:
                # Обновляем статус пользователя как онлайн
                user = request.user
                user.last_activity = timezone.now()
                user.is_online = True
                user.save()