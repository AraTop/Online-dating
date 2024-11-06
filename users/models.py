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
    is_in_chat = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)  # Поле для альбома по умолчанию
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos", blank=True, null=True)
    image = models.ImageField(upload_to="photos/")
    description = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo in {self.album.title if self.album else 'No Album'}"