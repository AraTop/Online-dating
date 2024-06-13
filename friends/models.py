from django.db import models
from users.models import User

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_list')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of_list')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f'{self.user} -> {self.friend} ({self.status})'
    