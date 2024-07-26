from django.contrib import admin
from .models import Interest, UserProfile, UserAction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_interests', 'age', 'gender', 'looking_for', 'search_night_partner')
    
    def display_interests(self, obj):
        return ", ".join(interest.name for interest in obj.interests.all())
    display_interests.short_description = 'Interests'


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver', 'likes', 'dislikes', 'hide')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
