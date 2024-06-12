from django.db import models
from django.contrib.auth.models import AbstractUser

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=11, verbose_name='Номер телефона', unique=True,)
    email = models.EmailField(unique=True, verbose_name='Почта')
    first_name = models.CharField(max_length=40, verbose_name='Имя')
    last_name = models.CharField(max_length=40, verbose_name='Фамилия', **NULLABLE)
    surname = models.CharField(max_length=60, verbose_name='Отчествоо', **NULLABLE)
    nickname = models.CharField(max_length=10, verbose_name='Nick_name', unique=True,)
    balance = models.FloatField(verbose_name='Баланс', **NULLABLE, default=0)
    profile_icon = models.ImageField(upload_to='users/', verbose_name='Фотография профиля', **NULLABLE)
    description = models.TextField(verbose_name='Описание профиля', **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []