from django.urls import path
from main.views import home
from users import views
from main.apps import MainConfig


app_name = MainConfig.name

urlpatterns = [
   path('', home, name='home'),
]