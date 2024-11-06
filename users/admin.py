from django.contrib import admin
from users.models import Album, Photo, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'surname', 'balance', 'description', 'profile_icon', 'is_online', 'last_activity')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'description', 'is_default', 'created_at')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'image', 'description', 'uploaded_at')