from django.urls import path
from . import views
from .apps import FriendsConfig

app_name = FriendsConfig.name

urlpatterns = [
    path('add/<str:username>/', views.AddFriendView.as_view(), name='add_friend'),
    path('remove/<int:friend_id>/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('list/', views.FriendListView.as_view(), name='friend_list'),
]