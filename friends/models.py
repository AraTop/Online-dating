from django.db import models
from users.models import User

class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_list')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of_list')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"
    