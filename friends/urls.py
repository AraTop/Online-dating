from django.urls import path
from . import views
from .apps import FriendsConfig

app_name = FriendsConfig.name

urlpatterns = [
    path('add/<str:username>/', views.AddFriendView.as_view(), name='add_friend'),
    path('remove/<int:friend_id>/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('list/', views.FriendListView.as_view(), name='friend_list'),
    path('friend_request/', views.friend_requests, name='friend_request'),
    path('friend_add/<int:pk>/', views.friend_add, name='friend_add'),
]   