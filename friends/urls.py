from django.urls import path
from project import settings
from . import views
from .apps import FriendsConfig
from django.conf.urls.static import static

app_name = FriendsConfig.name

urlpatterns = [
    path('add/<int:pk>/', views.AddFriendView, name='add_friend'),
    path('remove/<int:friend_id>/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('list/', views.FriendListView.as_view(), name='friend_list'),
    path('friend_request/', views.friend_requests, name='friend_request'),
    path('friend_outgoing/', views.friend_outgoing, name='friend_outgoing'),
    path('friend_add/<int:pk>/', views.friend_add, name='friend_add'),
    path('friend_reject/<int:pk>/', views.friend_reject, name='friend_reject'),
]   
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
