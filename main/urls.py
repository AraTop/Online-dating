from django.urls import path
from main.views import home
from project import settings
from users import views
from main.apps import MainConfig
from django.conf.urls.static import static

app_name = MainConfig.name

urlpatterns = [
   path('', home, name='home'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
