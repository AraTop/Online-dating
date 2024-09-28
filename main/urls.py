from django.urls import path
from main.views import home
from project import settings
from main import views
from main.apps import MainConfig
from django.conf.urls.static import static

app_name = MainConfig.name

urlpatterns = [
   path('', home, name='home'),
   path('search_users/', views.search_users, name='search_users'),
   path('search_night_partner/', views.search_night_partner, name='search_night_partner'),
   path('like_dislike_user/<int:user_id>/<str:action>/', views.like_dislike_user, name='like_dislike_user'),
   path('profile_setup/', views.profile_setup, name='profile_setup'),
   path('hide/', views.hide, name='hide'),
   path('remove_hide/<int:user_id>/', views.remove_hide, name='remove_hide'),
   path('search_friends/', views.search_friends, name='search_friends'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
