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

    class Meta:
        unique_together = ('user', 'gender')
        verbose_name = 'Профиль для знакомств'
        verbose_name_plural = 'Профиль для знакомств'


class UserAction(models.Model):
    user = models.ForeignKey(User, related_name='user_actions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_actions', on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    hide = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'receiver')
        verbose_name = 'Действия пользователя'
        verbose_name_plural = 'Действия пользователей'
