from users.models import User
from django.db import models

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другой'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank=True, null=True)
    looking_for = models.CharField(max_length=15, blank=True, null=True)
    search_night_partner = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name
