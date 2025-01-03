from users.models import User
from django.db import models
from datetime import date


class Interest(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('name',)
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'


class UserProfile(models.Model):
    SEX_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ]
    ORIENTATION_CHOICES = [
        ('not_specified', 'Не указан'),
        ('Homosexuality', 'Гомосексуальность'),
        ('Bisexuality', 'Бисексуальность'),
        ('Asexuality', 'Асексуальность'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Interest, related_name='user_profiles')
    date_of_birth = models.DateField(blank=True, null=True)  # Дата рождения
    sex = models.CharField(max_length=15, choices=SEX_CHOICES, blank=True, null=True)
    from_age = models.IntegerField(blank=True, null=True)
    to_age = models.IntegerField(blank=True, null=True)
    orientation = models.CharField(max_length=15, choices=ORIENTATION_CHOICES, blank=True, null=True)
    looking_for = models.CharField(max_length=16, blank=True, null=True)
    search_night_partner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'sex')
        verbose_name = 'Профиль для знакомств'
        verbose_name_plural = 'Профиль для знакомств'
    
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


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
