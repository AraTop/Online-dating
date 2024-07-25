from django.contrib import admin
from .models import UserProfile, UserAction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'interests', 'age', 'gender', 'looking_for', 'search_night_partner')


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver', 'likes', 'dislikes', 'hide')