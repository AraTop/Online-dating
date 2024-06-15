from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('dialog/<int:user_id>/', views.dialog, name='dialog'),
]
