# Generated by Django 5.0.6 on 2024-11-03 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_remove_userprofile_age_userprofile_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='orientation',
            field=models.CharField(blank=True, choices=[('not_specified', 'Не указан'), ('Homosexuality', 'Гомосексуальность'), ('Bisexuality', 'Бисексуальность'), ('Asexuality', 'Асексуальность')], max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=15, null=True),
        ),
    ]