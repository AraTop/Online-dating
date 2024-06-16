from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('dialog/<int:user_id>/', views.dialog, name='dialog'),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),  # Edit message
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),  # Delete message
]
