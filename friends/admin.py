from django.contrib import admin
from friends.models import Friend


@admin.register(Friend)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')
