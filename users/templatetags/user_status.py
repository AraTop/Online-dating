from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.simple_tag
def get_user_status(user):
    if user.is_online:
        return "Online"
    if timezone.now() - user.last_activity < timedelta(minutes=5):
        return "Recently active"
    return f"Last seen {user.last_activity.strftime('%Y-%m-%d %H:%M:%S')}"
