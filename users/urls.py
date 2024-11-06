from django.urls import path
from project import settings
from users import views
from users.views import LoginView, LogoutView
from users.apps import UsersConfig
from django.conf.urls.static import static

app_name = UsersConfig.name

urlpatterns = [
   path('login/', LoginView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(), name='logout'),
   path('register/', views.RegisterView.as_view(), name='register'),
   path('settings/', views.ProfileView.as_view(), name='profile'),
   path('delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
   path('<int:pk>/', views.UserDetailView.as_view(), name='user_profile'),
   path('update_status/', views.update_status, name='update_status'),
   path('albums/add/', views.add_album, name='add_album'),
   path('albums/<int:album_id>/delete/', views.delete_album, name='delete_album'),
   path('photos/add/', views.add_photo, name='add_photo'),
   path('photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
