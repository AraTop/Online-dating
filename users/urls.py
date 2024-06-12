from django.urls import path
from users import views
from users.views import LoginView, LogoutView
from users.apps import UsersConfig


app_name = UsersConfig.name

urlpatterns = [
   path('login/', LoginView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(), name='logout'),
   path('register/', views.RegisterView.as_view(), name='register'),
   path('settings/', views.ProfileView.as_view(), name='profile'),
   path('delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
]