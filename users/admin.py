from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'surname', 'nickname', 'balance', 'description', 'profile_icon', 'is_online', 'last_activity')
