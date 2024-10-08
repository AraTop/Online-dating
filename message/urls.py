from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('dialog/<int:user_id>/', views.dialog, name='dialog'),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),  # Edit message
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),  # Delete message
    path('<int:user_id>/history/', views.get_message_history, name='get_message_history'),
    path('delete_chat/both/<int:user_id>/', views.delete_chat_for_both, name='delete_chat_for_both'),
]
