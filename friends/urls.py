from django.urls import path
from . import views

urlpatterns = [
    path('add/<str:username>/', views.AddFriendView.as_view(), name='add_friend'),
    path('remove/<int:pk>/', views.RemoveFriendView.as_view(), name='delete_friend'),
    path('list/', views.FriendListView.as_view(), name='friend_list'),
    path('<str:username>/', views.FriendDetailView.as_view(), name='friend_detail'),  # Маршрут для профиля друга
]