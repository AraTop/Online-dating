from django.db import models
from django.contrib.auth.models import AbstractUser

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Почта')
    first_name = models.CharField(max_length=40, verbose_name='Имя')
    last_name = models.CharField(max_length=40, verbose_name='Фамилия')
    surname = models.CharField(max_length=60, verbose_name='Отчество', **NULLABLE)
    balance = models.FloatField(verbose_name='Баланс', **NULLABLE, default=0)
    profile_icon = models.ImageField(upload_to='users/', verbose_name='Фотография профиля', **NULLABLE)
    description = models.TextField(verbose_name='Описание профиля', **NULLABLE)
    last_activity = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
