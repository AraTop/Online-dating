from django.db import models
from users.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}: {self.content[:20]}'

    class Meta:
        ordering = ['timestamp']

    @classmethod
    def get_dialog(cls, user1, user2):
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2) | models.Q(sender=user2, receiver=user1)
        ).order_by('timestamp')
