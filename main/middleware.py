from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from .models import UserProfile

class NightPartnerMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.filter(user=request.user).first()
            path = request.path

            if user_profile:
                if path == reverse('main:search_night_partner'):
                    # Устанавливаем search_night_partner в True, когда находимся на странице поиска
                    user_profile.search_night_partner = True
                    user_profile.save()
                    request.session['search_night_partner'] = True
                    
                elif 'search_night_partner' in request.session and not path.startswith('/users/update_status/'):
                    # Сброс search_night_partner, если пользователь покидает страницу поиска и не является запросом на обновление статуса
                    user_profile.search_night_partner = False
                    user_profile.save()
                    del request.session['search_night_partner']